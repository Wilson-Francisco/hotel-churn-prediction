import unittest
import sqlite3
import pandas as pd

class TestSQLPipeline(unittest.TestCase):

    def setUp(self):
        """Cria um banco SQLite em memória e insere dados mínimos para testar as queries."""
        self.con = sqlite3.connect(":memory:")
        self.cursor = self.con.cursor()

        # 1. Criação das tabelas base
        self.cursor.execute("""
            CREATE TABLE users (
                user_id TEXT, user_gender TEXT, age_group TEXT, traveller_type TEXT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE hotels (
                hotel_id TEXT, hotel_name TEXT, city TEXT, country TEXT, star_rating REAL, value_for_money_base REAL
            );
        """)
        self.cursor.execute("""
            CREATE TABLE reviews (
                review_id TEXT, review_date TEXT, user_id TEXT, hotel_id TEXT, 
                score_overall REAL, score_cleanliness REAL, score_comfort REAL, score_facilities REAL, review_text TEXT
            );
        """)

        # 2. Inserção de dados fictícios mínimos para não dar erro de join
        self.cursor.execute("INSERT INTO users VALUES ('u1', 'F', '25-34', 'Business');")
        self.cursor.execute("INSERT INTO hotels VALUES ('h1', 'Hotel Teste', 'SP', 'Brasil', 4.0, 8.0);")
        self.cursor.execute("INSERT INTO reviews VALUES ('r1', '2026-01-10', 'u1', 'h1', 9.0, 9.0, 9.0, 8.5, 'Ótimo');")
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_geracao_da_abt_completa(self):
        """Executa as duas queries reais enviadas por você para garantir que não há erros de sintaxe."""
        
        # Geração do Book de Variáveis
        # Substituímos o parâmetro dinâmico  por uma data fixa de teste '2026-01-15'
        query_book = """
        CREATE TABLE tb_books_user AS
        WITH tb_variaveis AS (
            SELECT
                '2026-01-15' AS ref_date,
                t1.review_date, t1.review_id, t1.user_id, t2.hotel_name, t2.city, t2.country,
                (julianday('2026-01-15') - julianday(MAX(t1.review_date))) AS ultima_review,
                COUNT(t1.review_id) as freq_total_reviews,
                SUM(CASE WHEN t1.review_date >= date('2026-01-15', '-90 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_90_dias,
                SUM(CASE WHEN t1.review_date >= date('2026-01-15', '-180 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_180_dias,
                SUM(CASE WHEN t1.review_date >= date('2026-01-15', '-365 days') THEN 1 ELSE 0 END) AS freq_reviews_ultimos_365_dias,
                AVG(t1.score_overall) AS sat_media_score_overall,
                AVG(t1.score_cleanliness) AS sat_media_score_limpeza,
                AVG(t1.score_comfort) AS sat_media_score_conforto,
                AVG(t1.score_facilities) AS sat_media_score_comodidades,
                COUNT(DISTINCT t1.hotel_id) AS div_hoteis_diferentes,
                COUNT(DISTINCT t2.city) AS div_cidades_diferentes,
                AVG(t2.star_rating) AS div_media_estrelas_hoteis,
                AVG(t2.value_for_money_base) AS media_custo_beneficio,
                (julianday('2026-01-15') - julianday(MIN(t1.review_date))) AS temp_dias_desde_primeira_review
            FROM reviews as t1
            JOIN hotels AS t2 ON t1.hotel_id = t2.hotel_id
            WHERE t1.review_date < '2026-01-15' AND t1.review_date >= date('2026-01-15', '-365 days')
            GROUP BY t1.user_id
        )
        SELECT
            t2.*, t1.user_gender, t1.age_group, t1.traveller_type
        FROM users AS t1
        LEFT JOIN tb_variaveis AS t2 ON t1.user_id = t2.user_id
        WHERE t2.review_date BETWEEN date('2026-01-15', '-365 days') AND '2026-01-15'
        GROUP BY t1.user_id;
        """
        
        # Executa a primeira query 
        try:
            self.cursor.execute(query_book)
            self.con.commit()
        except Exception as e:
            self.fail(f"A sua query do Book de Variáveis falhou: {e}")

        # Criação da Tabela ABT final
        query_abt = """
        CREATE TABLE tb_abt_churn AS  
        WITH tb_reviews_user AS (
            SELECT t1.review_id, t1.review_date, t1.user_id, t1.review_text, 1 AS ativo
            FROM reviews as t1
            GROUP BY t1.review_id, t1.user_id
        ) 
        SELECT   
            t1.*, t2.review_text,
            CASE WHEN t2.user_id IS NULL THEN 1 ELSE 0 END AS target_churn
        FROM tb_books_user AS t1
        LEFT JOIN tb_reviews_user AS t2 ON t1.user_id = t2.user_id
        AND t2.review_date BETWEEN t1.ref_date AND date(t1.ref_date, '+365 days')
        WHERE t1.ref_date < '2026-12-31'
        GROUP BY t1.review_id, t1.user_id
        ORDER BY t1.ref_date;
        """

        # Executa a segunda query
        try:
            self.cursor.execute(query_abt)
            self.con.commit()
        except Exception as e:
            self.fail(f"A sua query de criação da ABT falhou: {e}")

        # Valida se a tabela ABT realmente nasceu e possui a coluna target_churn
        df_resultado = pd.read_sql_query("SELECT * FROM tb_abt_churn", self.con)
        self.assertIn("target_churn", df_resultado.columns, "A ABT foi gerada mas falta a coluna 'target_churn'!")


if __name__ == "__main__":
    unittest.main()

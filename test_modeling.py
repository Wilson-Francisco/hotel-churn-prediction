import unittest
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from feature_engine.encoding import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline


# Copiamos a função de sentimento exatamente igual ao seu código para testá-la
def extrair_sentimento_vader(texto, sia):
    if str(texto).strip() == "":
        return 0.0
    scores = sia.polarity_scores(str(texto))
    return scores['compound']


class TestChurnModelingAndPredict(unittest.TestCase):

    def setUp(self):
        """Configura o ambiente com dados fictícios simulando a ABT real."""
        self.sia = SentimentIntensityAnalyzer()
        
    
        self.features_numericas = [
            'sat_media_score_overall', 'sentimento_review', 'sat_media_score_limpeza',
            'sat_media_score_conforto', 'sat_media_score_comodidades', 'freq_total_reviews'
        ]
        self.features_categoricas = ['hotel_name', 'user_gender', 'age_group', 'traveller_type']
        self.features = self.features_numericas + self.features_categoricas
        
        # Dados Fictícios Mínimos para Treino 
        self.df_treino_ficticio = pd.DataFrame ({
            'sat_media_score_overall': [9.0, 5.0, 8.5, 4.0, 9.5, 6.0],
            'sentimento_review': [0.8, -0.5, 0.6, -0.7, 0.9, 0.0],
            'sat_media_score_limpeza': [9.0, 4.0, 8.0, 5.0, 10.0, 6.0],
            'sat_media_score_conforto': [9.0, 5.0, 8.0, 4.0, 9.0, 7.0],
            'sat_media_score_comodidades': [8.5, 5.0, 8.0, 5.0, 9.5, 6.5],
            'freq_total_reviews':[1, 4.0, 2.0, 7.0, 3, 0],
            'hotel_name': ['Hotel A', 'Hotel B', 'Hotel C', 'Hotel A', 'Hotel B', 'Hotel C'],
            'user_gender': ['F', 'M', 'F', 'M', 'F', 'M'],
            'age_group': ['25-34', '35-44', '45-54', '25-34', '35-44', '45-54'],
            'traveller_type': ['Business', 'Leisure', 'Business', 'Leisure', 'Business', 'Leisure'],
            'target_churn': [0, 1, 0, 1, 0, 1]
        })

        # Configuração do Pipeline
        self.pipeline = Pipeline(steps=[
            ("onehot", OneHotEncoder(variables=self.features_categoricas)),
            ("norm", MinMaxScaler()),
            ("smote", SMOTE(random_state=42, k_neighbors=1)),
            ("clf_tree", DecisionTreeClassifier(max_depth=5, random_state=42))
        ])

    def test_extrair_sentimento_vader(self):
        """Valida se a função do VADER pontua corretamente textos vazios, positivos e negativos."""
        # Teste com texto vazio (deve retornar 0.0 conforme sua regra)
        self.assertEqual(extrair_sentimento_vader("", self.sia), 0.0)
        self.assertEqual(extrair_sentimento_vader(None, self.sia), 0.0)
        
        # Teste com texto nitidamente positivo (deve ser > 0)
        score_positivo = extrair_sentimento_vader("Excellent hotel, very clean and comfortable!", self.sia)
        self.assertGreater(score_positivo, 0.0)
        
        # Teste com texto nitidamente negativo (deve ser < 0)
        score_negativo = extrair_sentimento_vader("Terrible service, dirty room and bad experience.", self.sia)
        self.assertLess(score_negativo, 0.0)

    def test_pipeline_fit_and_predict_proba_flow(self):
        """Valida o fluxo completo de treino e predição por probabilidade."""
        X_train = self.df_treino_ficticio[self.features]
        y_train = self.df_treino_ficticio['target_churn']
        
        # Testa o treinamento
        try:
            self.pipeline.fit(X_train, y_train)
        except Exception as e:
            self.fail(f"O pipeline quebrou no treinamento (.fit): {e}")
            
        # Dados Fictícios de Inferência
        df_oot_ficticio = pd.DataFrame({
            'sat_media_score_overall': [8.0, 4.5],
            'sentimento_review': [0.5, -0.4],
            'sat_media_score_limpeza': [8.0, 4.0],
            'sat_media_score_conforto': [8.5, 5.0],
            'sat_media_score_comodidades': [7.0, 4.5],
            'freq_total_reviews': [16, 3],
            'hotel_name': ['Hotel A', 'Hotel B'],
            'user_gender': ['M', 'F'],
            'age_group': ['35-44', '25-34'],
            'traveller_type': ['Leisure', 'Business']
        })
        
        # Testa a predição por probabilidade
        try:
            # Captura a probabilidade da classe 1 (Churn)
            predicao_proba = self.pipeline.predict_proba(df_oot_ficticio[self.features])[:, 1]
        except Exception as e:
            self.fail(f"O pipeline carregado quebrou ao rodar o predict_proba: {e}")
            
        # Validações de saída (Asserts)
        self.assertEqual(len(predicao_proba), len(df_oot_ficticio), "O número de saídas deve ser igual ao de entradas.")
        

    def test_pipeline_com_valores_nulos_na_predicao(self):
        """Garante que o pipeline não quebra se novos dados vierem com NaN."""
        X_train = self.df_treino_ficticio[self.features]
        y_train = self.df_treino_ficticio['target_churn']
        
        # Treina o pipeline normalmente
        self.pipeline.fit(X_train, y_train)
        
        # Simulando dados reais de produção com valores nulos (NaN) nas notas
        df_oot_com_nulos = pd.DataFrame({
            'sat_media_score_overall': [np.nan, 4.5],      
            'sentimento_review': [0.5, np.nan],            
            'sat_media_score_limpeza': [8.0, 4.0],
            'sat_media_score_conforto': [np.nan, 5.0],     
            'sat_media_score_comodidades': [7.0, 4.5],
            'freq_total_reviews':[np.nan, 3],
            'hotel_name': ['Hotel A', 'Hotel B'],
            'user_gender': ['M', 'F'],
            'age_group': ['35-44', '25-34'],
            'traveller_type': ['Leisure', 'Business']
        })
        
        # O Imputer deve preencher os nulos com a mediana do treino automaticamente.
        try:
            predicao_proba = self.pipeline.predict_proba(df_oot_com_nulos[self.features])[:, 1]
        except Exception as e:
            self.fail(f"O pipeline quebrou ao receber valores nulos (NaN): {e}")

        # Garante que todas as saídas são probabilidades válidas entre 0.0 e 1.0
        for proba in predicao_proba:
            self.assertGreaterEqual(proba, 0.0)
            self.assertLessEqual(proba, 1.0)


if __name__ == "__main__":
    unittest.main()

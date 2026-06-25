import pandas as pd
import os 
import sqlalchemy


EP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(EP_DIR)       # src/
BASE_DIR = os.path.dirname(SRC_DIR)     # raiz do projeto 
DATA_DIR = os.path.join(BASE_DIR, 'data')
SQL_DIR = os.path.join(SRC_DIR, 'sql_etl')

def import_query(path, **kwards):
    if 'encoding' not in kwards:
        kwards['encoding'] = 'utf-8'
    
    with open(path, 'r', **kwards) as file_open:
        result = file_open.read()
    return result


def connect_db():
    # Garante que a pasta 'data' exista antes de tentar abrir ou criar o arquivo SQLite
    os.makedirs(DATA_DIR, exist_ok=True)
    db_path = os.path.join(DATA_DIR, 'booking_db.sqlite')
    return sqlalchemy.create_engine("sqlite:///" + db_path)

query_path = os.path.join(SQL_DIR, 'query_1.sql')

query = import_query(query_path)
query = query.format(date='2025-12-31')


con = connect_db()

with con.connect() as connection:
    try:
        connection.execute(sqlalchemy.text("delete from tb_books_user where ref_date = '{date}'".format(date='2025-12-31')))
        connection.commit()
    except Exception:
        print('Nada a ser deletado')


    try:
        base_query = 'create table tb_books_user as\n {query}'
        connection.execute(sqlalchemy.text(base_query.format(query=query)))
        connection.commit()
        print('Criando tabela...')
    except Exception:
        base_query = 'insert into tb_books_user \n {query}'
        connection.execute(sqlalchemy.text(base_query.format(query=query)))
        connection.commit()
        print('Inserindo dados novos na tabela...')

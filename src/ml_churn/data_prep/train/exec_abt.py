import os 
import sqlalchemy
from sqlalchemy import text # 1. Importe a função text

TRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PREP_DIR = os.path.dirname(TRAIN_DIR)       # src/
BASE_DIR = os.path.dirname(DATA_PREP_DIR)     # raiz do projeto 
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data') 

engine = sqlalchemy.create_engine("sqlite:///" + os.path.join(DATA_DIR, 'booking_db.sqlite'))

with open(os.path.join(TRAIN_DIR, 'abt.sql'), 'r') as open_file:
    query = open_file.read()

# 2. Abra a conexão de forma segura
with engine.connect() as connection:
    # 3. Inicie uma transação para garantir que tudo execute ou falhe junto
    with connection.begin():
        for i in query.split(";")[:-1]:
            # Remove espaços em branco ou quebras de linha vazias antes de executar
            sql_command = i.strip()
            if sql_command:
                # 4. Use text() para envelopar a query
                connection.execute(text(sql_command))

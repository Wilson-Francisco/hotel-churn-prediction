import os 
import pandas as pd
import sqlalchemy
from sqlalchemy import text # 1. Importe a função text

TRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
MODELING_DIR = os.path.dirname(TRAIN_DIR)       # src/
BASE_DIR = os.path.dirname(MODELING_DIR)     # raiz do projeto 

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data') 

engine = sqlalchemy.create_engine("sqlite:///" + os.path.join(DATA_DIR, 'booking_db.sqlite'))



abt = pd.read_sql_table('tb_abt_churn', engine)

print(abt.head(10))
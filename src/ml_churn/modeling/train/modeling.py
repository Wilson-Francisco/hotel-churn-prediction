import os 
import pandas as pd
import sqlalchemy


TRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
MODELING_DIR = os.path.dirname(TRAIN_DIR)       # src/
BASE_DIR = os.path.dirname(MODELING_DIR)     # raiz do projeto 

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data') 

engine = sqlalchemy.create_engine("sqlite:///" + os.path.join(DATA_DIR, 'booking_db.sqlite'))


# tabela ABT para todas as analises
abt = pd.read_sql_table('tb_abt_churn', engine)


df_oot = abt[abt['ref_date'] == abt['ref_date'].max()].copy() # filtrando base out of time

df_abt = abt[abt['ref_date'] < abt['ref_date'].max()].copy() # filtrando base ABT

print('tabela out of time: ', df_oot.shape)
print(df_oot['target_churn'].mean())
print('tabela ABT: ', df_abt.shape)
print(df_abt['target_churn'].mean())

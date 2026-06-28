import os 
import pandas as pd
import sqlalchemy
import mlflow
import mlflow.sklearn
from nltk.sentiment.vader import SentimentIntensityAnalyzer



TRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
MODELING_DIR = os.path.dirname(TRAIN_DIR)       
BASE_DIR = os.path.dirname(MODELING_DIR)     

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data') 

con = sqlalchemy.create_engine("sqlite:///" + os.path.join(DATA_DIR, 'booking_db.sqlite'))


# tabela ABT para todas as analises
abt = pd.read_sql_table('tb_abt_churn', con)


df_oot = abt[abt['ref_date'] == abt['ref_date'].max()].copy() # filtrando base out of time

# Converte a coluna review_date para datetime
df_oot['review_date'] = pd.to_datetime(df_oot['review_date'], format='%Y-%m-%d')

df_oot.columns = [str(coluna_nome) for coluna_nome in df_oot.columns]

print(df_oot.shape)

# Baixa o dicionário de regras do VADER (focado em avaliações/sentimentos)
# nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


# Tratamento dos nulos coluna review_text
df_oot['review_text'] = df_oot['review_text'].fillna("")

# TRATAMENTO E EXTRAÇÃO DE SENTIMENTO
def extrair_sentimento(texto):
    if str(texto).strip() == "":
        return 0.0 # Texto vazio recebe score neutro
    
    scores = sia.polarity_scores(str(texto))
    return scores['compound'] # Retorna a nota geral de sentimento (-1 a +1)

print("Extraindo o sentimento dos textos...")
# Aplica a função em toda a base abt
df_oot['sentimento_review'] = df_oot['review_text'].apply(extrair_sentimento)


# As features numéricas e categóricas selecionadas
features_numericas = [
    'sat_media_score_overall', 'sentimento_review', 'sat_media_score_limpeza',
    'sat_media_score_conforto', 'sat_media_score_comodidades', 'freq_total_reviews'
]

features_categoricas = ['hotel_name', 'user_gender', 'age_group', 'traveller_type']

# Concatenacao das features
features = features_numericas + features_categoricas


# Acessar o MLflow
mlflow.set_tracking_uri("http://localhost:5000")


# Capturar sempre a versão mais recente do modelo no mlfow
client = mlflow.client.MlflowClient()
version = max([int(i.version) for i in client.get_latest_versions("Modelo_clf_tree_encoder")])


# Importar do modelo do mlflow
model_clf_tree = mlflow.sklearn.load_model(f"models:/Modelo_clf_tree_encoder/{version}")


# Predição do modelo
predicao = model_clf_tree.predict_proba(df_oot[features])[:,1]
df_oot["score_churn_hotel"] = predicao


# Enviando os dados para o banco de dados
df_oot[['user_id', 'score_churn_hotel']].to_sql("tb_score_churn_hotel", con, if_exists='replace', index=False)


print(df_oot[['user_id', 'score_churn_hotel']].head(20))



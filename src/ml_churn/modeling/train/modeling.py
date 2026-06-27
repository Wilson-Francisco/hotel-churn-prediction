import os 
import pandas as pd
import sqlalchemy
import numpy as np
import matplotlib.pyplot as plt
import nltk
from imblearn.over_sampling import SMOTE
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from feature_engine.encoding import OneHotEncoder
from sklearn import metrics
from imblearn.pipeline import Pipeline 
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


TRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
MODELING_DIR = os.path.dirname(TRAIN_DIR)       # src/
BASE_DIR = os.path.dirname(MODELING_DIR)     # raiz do projeto 

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data') 

engine = sqlalchemy.create_engine("sqlite:///" + os.path.join(DATA_DIR, 'booking_db.sqlite'))


# tabela ABT para todas as analises
abt = pd.read_sql_table('tb_abt_churn', engine)


df_oot = abt[abt['ref_date'] == abt['ref_date'].max()].copy() # filtrando base out of time

df_abt = abt[abt['ref_date'] < abt['ref_date'].max()].copy() # filtrando base ABT

df_abt.drop(['ref_date', 'review_id', 'user_id'],axis=1, inplace=True )


# Converte a coluna review_date para datetime
df_abt['review_date'] = pd.to_datetime(df_abt['review_date'], format='%Y-%m-%d')

df_abt.columns = [str(coluna_nome) for coluna_nome in df_abt.columns]

# Baixa o dicionário de regras do VADER (focado em avaliações/sentimentos)
# nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


# Tratamento dos nulos coluna review_text
df_abt['review_text'] = df_abt['review_text'].fillna("")

# TRATAMENTO E EXTRAÇÃO DE SENTIMENTO
def extrair_sentimento(texto):
    if str(texto).strip() == "":
        return 0.0 # Texto vazio recebe score neutro
    
    scores = sia.polarity_scores(str(texto))
    return scores['compound'] # Retorna a nota geral de sentimento (-1 a +1)

print("Extraindo o sentimento dos textos...")
# Aplica a função em toda a base abt
df_abt['sentimento_review'] = df_abt['review_text'].apply(extrair_sentimento)


# Separando as variáveis categóricas
variaveis_categoricas = []
for i in df_abt.columns[0:14].tolist():
        if df_abt.dtypes[i] == 'object' or df_abt.dtypes[i] == 'category':
            variaveis_categoricas.append(i)

# As features numéricas e categóricas selecionadas
features_numericas = [
    'sat_media_score_overall', 'sentimento_review', 'sat_media_score_limpeza',
    'sat_media_score_conforto', 'sat_media_score_comodidades', 'freq_total_reviews'
]

features_categoricas = ['hotel_name', 'user_gender', 'age_group', 'traveller_type']

# Concatenacao das features
features = features_numericas + features_categoricas
target = 'target_churn'


# Cria o encoder e aplicar OneHotEncoder# Cria o encoder e aplicar OneHotEncoder
onehot = OneHotEncoder(variables=features_categoricas)


# Normalizar as variáveis
norm = MinMaxScaler()


# Balaceamento dos dados
smote = SMOTE(random_state=42)

target = 'target_churn'

# Dividir os dados em treino e teste para iniciar a fase de criação do modelo
X_train, X_test, y_train, y_test = train_test_split(df_abt[features], df_abt[target] , test_size = 0.2, random_state = 42)


# Modelo de árvore de classificador de Árvore de Decisão
clf_tree = tree.DecisionTreeClassifier(max_depth=5, random_state = 42)
 
# Pipeline com todos objetos
model_pipeline = Pipeline(steps = [("onehot", onehot),
                                   ("norm ", norm ),
                                   ("smote", smote),
                                   ("clf_tree", clf_tree)])


# Ajustando o modelo
model_pipeline.fit(X_train[features], y_train)                                  


print(X_train[features].head())  

 
# Salvando o algoritmo
model = pd.Series(
    {
        "model": model_pipeline,
        "features": features
    } )


# Métricas de treino do modelo
pred_train = model["model"].predict(X_train[features])
pred_proba_train = model["model"].predict_proba(X_train[features])[:,1]

# Calcular acuracia do modelo de treino
scores_train = model["model"].score(X_train[features], y_train)
print(f"Acurácia em Treinamento: {scores_train}")

# Calcular curva ROC do modelo de treino
scores_roc_auc_train = metrics.roc_auc_score(y_train, pred_proba_train)
print(f"Curva ROC em Treinamento: {scores_roc_auc_train}")

# Métricas de teste do modelo
pred_test = model["model"].predict(X_test[features])
pred_proba_test = model["model"].predict_proba(X_test[features])[:,1]

# Calcular acuracia do modelo de teste
scores_test = model["model"].score(X_test[features], y_test)
print(f"Acurácia em Test: {scores_test}")

# Calcular curva ROC do modelo de teste
scores_auc_test = metrics.roc_auc_score(y_test, pred_proba_test)
print(f"Curva ROC em Test:{scores_auc_test}")

# Treino da Curva ROC
roc_curve_train = metrics.roc_curve(y_train, pred_proba_train)

# Teste da Curva ROC
roc_curve_test = metrics.roc_curve(y_test, pred_proba_test)

# Gráfico da curva ROC
plt.plot(roc_curve_train[0], roc_curve_train[1])
plt.plot(roc_curve_test[0], roc_curve_test[1])
plt.grid(True)
plt.plot([0,1],[0,1], "--", color="black")
plt.title("Curva ROC")
plt.ylabel("Sensibilidade")
plt.xlabel("1 - Especificidade")
plt.legend(
    [
        f"Treino: {100*scores_train:.2f}%",
        f"Teste: {100*scores_test:.2f}%"
    ])

plt.show() 

# Feature_importance do modelo
features_names = (model.iloc[0][0].transform(X_train[features]).columns.tolist())
feature_importance = pd.Series(model.iloc[0][-1].feature_importances_,
                               index=features_names)
feature_importance.sort_values(ascending=False)
print(feature_importance.sort_values(ascending=False))


















# 🏨 Hotel Churn Prediction Project

Este projeto implementa uma esteira completa de Engenharia e Ciência de Dados para prever o risco de *churn* (cancelamento/abandono) de clientes de redes hoteleiras. O sistema engloba desde a extração de variáveis históricas e análise de sentimento de texto até o monitoramento de experimentos e deploy contínuo.

---

## 📊 Origem dos Dados & Principais Insights (EDA)

### 🗃️ Fonte de Dados
Os dados utilizados neste projeto foram obtidos a partir do **Hotel Reviews Dataset** disponível publicamente no **Kaggle** através do link:
👉 [Kaggle - Hotel Reviews Dataset](https://www.kaggle.com/datasets/antonyayman/hotel-reviews-dataset)

### 💡 Descobertas da Análise Exploratória
Embora a taxa de churn geral da base seja considerada baixa (**1,33%**), a análise exploratória revelou padrões críticos de comportamento:
* **Gargalos Geográficos:** O churn **duplica** se o cliente se hospedar em hotéis localizados em **Amsterdã, Seul ou Nova York**.
* **Perfil de Risco:** O público mais propenso a abandonar a plataforma são **mulheres ou pessoas acima de 55 anos que viajam sozinhas (Solo)**.
* **Gatilho Emocional:** A queda no score de sentimento das reviews textuais é o principal indicador antecedente de churn. Esse descontentamento é fortemente influenciado pela **percepção de falta de limpeza** nos hotéis.

---

## 🛠️ Arquitetura do Pipeline do Modelo
O modelo utiliza um classificador baseado em **Árvore de Decisão** (`DecisionTreeClassifier`), encapsulado dentro de um pipeline dinâmico e robusto da biblioteca `imblearn` para garantir a consistência dos dados tanto no treino quanto na predição:

1. **Tratamento de Nulos (`MeanMedianImputer`):** Preenche valores numéricos ausentes (`NaN`) com a mediana do treino, evitando quebras em produção.
2. **Codificação Categórica (`OneHotEncoder`):** Transforma variáveis textuais em colunas binárias.
3. **Normalização (`MinMaxScaler`):** Escala os dados para o intervalo.
4. **Balanceamento de Classes (`SMOTE`):** Devido ao baixo volume de churn (1,33%), aplica sobreamostragem sintética apenas na fase de treino para balancear a base.
5. **Classificador (`DecisionTreeClassifier`):** Árvore configurada com profundidade máxima de 5 para evitar *overfitting*.

### 📋 Features Utilizadas no Modelo (10 Variáveis)
* **Numéricas:** `sat_media_score_overall`, `sentimento_review` (extraído via VADER Lexicon), `sat_media_score_limpeza`, `sat_media_score_conforto`, `sat_media_score_comodidades`, `freq_total_reviews`.
* **Categóricas:** `hotel_name`, `user_gender`, `age_group`, `traveller_type`.

---

## ⚙️ Estrutura de Código do Ecossistema

* **`modeling.py`:** Carrega os dados históricos do SQLite, aplica a extração de sentimento textual via `NLTK VADER`, realiza a divisão treino/teste, executa o `.fit()` do pipeline, calcula a importância das 43 variáveis expandidas e registra tudo no **MLflow Tracking**.
* **`predict.py`:** Acessa o registro do MLflow, faz o download automático da versão mais recente do modelo, realiza a predição probabilística (`predict_proba`) sobre a base *Out of Time* (OOT) e salva os scores de propensão diretamente na tabela `tb_score_churn_hotel` do banco de dados.

---

## 🗄️ Engenharia de Dados (Estrutura SQL)
A base de modelagem (ABT) é construída em duas etapas automatizadas dentro do SQLite (`booking_db.sqlite`):
1. **Book de Variáveis (`tb_books_user`):** Agrupa o comportamento de consumo, volumetria, frequência e médias de satisfação do usuário em janelas móveis de até 365 dias retroativos.
2. **Tabela Analítica Base (`tb_abt_churn`):** Realiza um *Left Join* com janelas futuras de `+365 dias`. Caso o usuário não possua interações no período seguinte, a coluna `target_churn` é definida como **1** (Churn), caso contrário **0** (Ativo).

---

## 🚀 Infraestrutura de CI/CD (GitHub Actions)
O projeto conta com uma esteira de automação profissional descrita em `.github/workflows/pipeline.yml`:

* **Continuous Integration (CI):** 
  * Instala o ambiente isolado utilizando o arquivo `requirements.txt`.
  * Executa o arquivo `test_database.py` para criar um banco em memória e testar a sintaxe SQL completa do Book e da ABT.
  * Executa o arquivo `test_modeling.py` (Testes Unitários) para testar o pipeline e garantir resiliência contra valores nulos e novas categorias de texto.
* **Continuous Delivery (CD):** 
  * Se o CI passar com sucesso, prepara o modelo para ser promovido para o ambiente produtivo de inferência.

---

## 💻 Como Executar o Projeto

1. **Instale as dependências com versões fixadas:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Execute os Testes de Validação da Esteira:**
   ```bash
   python -m unittest test_database.py
   python -m unittest test_modeling.py
   ```
3. **Inicie o Servidor do MLflow local para rastreamento:**
   ```bash
   mlflow server --host 127.0.0.1 --port 5000
   ```
4. **Execute o Treinamento do Modelo:**
   ```bash
   python modeling.py
   ```

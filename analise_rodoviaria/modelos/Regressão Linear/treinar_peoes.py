import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Caminho para o dataset
caminho_dataset = '../../datasets/melbourne_pedestrians.csv'

# 1. Carregar dados (low_memory=False resolve o aviso amarelo)
print("A carregar dataset de peões...")
df = pd.read_csv(caminho_dataset, low_memory=False)

# LIMPEZA DE DADOS
print("A limpar valores em falta (NaN)...")
df = df.dropna(subset=['date_time', 'sensor_id', 'hourly_counts']) # limpamos linhas que tem campos em branco
# isto e feito para que os dados depois acabem por ser iguais para todos
# pois para a RL e obigatorio fazer isto

print("A preparar dados...")

# 3. Extrair características
df['date_time'] = pd.to_datetime(df['date_time'])
df['hour'] = df['date_time'].dt.hour
df['day_of_week'] = df['date_time'].dt.dayofweek

features = ['hour', 'day_of_week', 'sensor_id']
X = df[features]
y = df['hourly_counts']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Treinar modelo
print("A treinar Regressão Linear...")
modelo = LinearRegression()
modelo.fit(X_train, y_train)

joblib.dump(modelo, 'modelo_peoes_lr.pkl')
print("Ficheiro 'modelo_peoes_lr.pkl' gerado!")
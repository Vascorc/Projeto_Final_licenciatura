import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# Caminho para o dataset
caminho_dataset = '../../datasets/melbourne_pedestrians.csv'

# Carregar dados
print("A carregar dataset de peões...")
df = pd.read_csv(caminho_dataset)

# LIMPEZA DE DADOS
print("A limpar valores em falta (NaN)...")
df = df.dropna(subset=['date_time', 'sensor_id', 'hourly_counts']) # limpamos linhas que tem campos em branco
# isto e feito para que os dados depois acabem por ser iguais para todos
# pois para a RL e obigatorio fazer isto

print("A preparar dados...")
df['date_time'] = pd.to_datetime(df['date_time'])
df['hour'] = df['date_time'].dt.hour
df['day_of_week'] = df['date_time'].dt.dayofweek

features = ['hour', 'day_of_week', 'sensor_id']
X = df[features]
y = df['hourly_counts']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo
print("A treinar Random Forest...")
modelo = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
modelo.fit(X_train, y_train)

# Guardar
joblib.dump(modelo, 'modelo_peoes_rf.pkl')
print("Ficheiro 'modelo_peoes_rf.pkl' gerado")

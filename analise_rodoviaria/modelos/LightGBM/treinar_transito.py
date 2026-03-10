import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# Caminho para o dataset
caminho_dataset = '../../datasets/Metro_Interstate_Traffic_Volume.csv'

# Carregar dados
print("A carregar dataset de trânsito...")
df = pd.read_csv(caminho_dataset)

print("A preparar dados...")
df['date_time'] = pd.to_datetime(df['date_time'])
df['hour'] = df['date_time'].dt.hour
df['day_of_week'] = df['date_time'].dt.dayofweek

features = ['hour', 'day_of_week', 'temp', 'rain_1h']
X = df[features]
y = df['traffic_volume']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo
print("A treinar modelo LightGBM...")
modelo = lgb.LGBMRegressor(random_state=42)
modelo.fit(X_train, y_train)

# Guardar
joblib.dump(modelo, 'modelo_transito_lgbm.pkl')
print("Ficheiro 'modelo_transito_lgbm.pkl' gerado")

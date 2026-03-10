import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

# 1. Carregar Dados de Trânsito
print("A carregar dados de trânsito...")
df = pd.read_csv('../datasets/Metro_Interstate_Traffic_Volume.csv')
df['date_time'] = pd.to_datetime(df['date_time'])
df['hour'] = df['date_time'].dt.hour
df['day_of_week'] = df['date_time'].dt.dayofweek

features = ['hour', 'day_of_week', 'temp', 'rain_1h']
X = df[features]
y = df['traffic_volume']

# Mesmo random_state=42 garante avaliação justa
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Carregar os Modelos Treinados (ajusta os nomes se necessário)
print("A carregar os modelos...")
modelos = {
    'Regressão Linear': joblib.load('Regressão Linear/modelo_transito_lr.pkl'),
    'Random Forest': joblib.load('Random Forest/modelo_transito_rf.pkl'),
    'LightGBM': joblib.load('LightGBM/modelo_transito_lgbm.pkl')
}

resultados_mae = []
resultados_r2 = []
nomes = list(modelos.keys())

# 3. Avaliar Modelos
for nome, modelo in modelos.items():
    previsoes = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)
    
    resultados_mae.append(mae)
    resultados_r2.append(r2)
    print(f"[{nome}] MAE: {mae:.2f} | R2: {r2:.4f}")

# 4. Gerar Gráficos
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Comparação de Modelos - Trânsito Automóvel', fontsize=16, fontweight='bold', color='#003874')

# Gráfico de Erro (MAE)
ax1.bar(nomes, resultados_mae, color=['#FF9999', '#66B2FF', '#99FF99'])
ax1.set_title('Erro Médio Absoluto (MAE) ↓')
ax1.set_ylabel('Carros de Erro')
for i, v in enumerate(resultados_mae):
    ax1.text(i, v + (max(resultados_mae)*0.02), f"{v:.1f}", ha='center', fontweight='bold')

# Gráfico de Precisão (R2)
ax2.bar(nomes, resultados_r2, color=['#FF9999', '#66B2FF', '#99FF99'])
ax2.set_title('Precisão ($R^2$ Score) ↑')
ax2.set_ylabel('Score (0 a 1)')
ax2.set_ylim(0, 1.1)
for i, v in enumerate(resultados_r2):
    ax2.text(i, v + 0.02, f"{v:.3f}", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_comparacao_transito.png', dpi=300)
print("Gráfico 'grafico_comparacao_transito.png' guardado")
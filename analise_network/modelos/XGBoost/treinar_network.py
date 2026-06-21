import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import gc

# --- CONFIGURAÇÃO ---
caminho_dataset = '../../datasets/dataset_treino.csv' 

print("🚀 A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (XGBOOST PURO)...")
print("1. A carregar o dataset balanceado...")

try:
    df = pd.read_csv(caminho_dataset, low_memory=False)
    
    # Substituímos a categoria 'Web-Attack' por 'Outros' pois essa categoria nao vai encaixar na nossa planilha de anomalias
    if 'categoria' in df.columns:
        df['categoria'] = df['categoria'].replace('Web-Attack', 'Outros')
        print("💡 Categoria 'Web-Attack' fundida com 'Outros' (Foco em IoT).")
    
    print(f"✅ Dados carregados! Pacotes analisados: {len(df)}")
except FileNotFoundError:
    print("❌ ERRO: Não encontrei o ficheiro csv balanceado.")
    exit()

# --- 2. ENGENHARIA DE FEATURES ---
print("2. A organizar labels...")
def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    if label == 'BENIGNTRAFFIC' or label == 'BENIGN': return 'Normal'
    if 'DDOS' in label: return 'DDoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DDoS-UDP/ICMP'
    if 'DOS' in label: return 'DoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DoS-UDP/ICMP'
    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    return 'Outros'
df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

print("3. A preparar dados para o XGBoost...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])
joblib.dump(le, 'label_encoder_categorias_xgb.pkl')

y = df['label_encoded']
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1, errors='ignore')

# --- FILTRO DE PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. TREINO ---
print("4. A dividir Treino (80%) / Teste (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. A treinar o Modelo XGBoost...")
modelo = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1)
modelo.fit(X_train, y_train)

# --- 5. GUARDAR ---
print("6. A guardar o cérebro da IA...")
joblib.dump(modelo, 'modelo_ciberseguranca_xgb.pkl')
print("✅ Ficheiro 'modelo_ciberseguranca_xgb.pkl' guardado com sucesso.")
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import gc

# --- CONFIGURAÇÃO ---
caminho_dataset1 = '../../datasets/Merged01.csv' 
caminho_dataset2 = '../../datasets/Merged02.csv' 

print("🚀 A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (XGBOOST)...")
print("1. A carregar datasets CICIoT2023 (isto pode demorar)...")

try:
    df1 = pd.read_csv(caminho_dataset1, low_memory=False)
    df2 = pd.read_csv(caminho_dataset2, low_memory=False)
    
    print("   -> A fundir os ficheiros...")
    df = pd.concat([df1, df2], ignore_index=True)
    
    del df1, df2
    gc.collect()
    
    print(f"Dados carregados! pacotes analisados: {len(df)}")

except FileNotFoundError:
    print("ERRO: Não encontrei os ficheiros csv.")
    exit()

# --- 2. ENGENHARIA DE FEATURES (AGRUPAMENTO POR MITIGAÇÃO) ---
print("2. A aplicar Lógica de Mitigação Inteligente...")

def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() # <-- O TRUQUE DE LIMPEZA
    
    if label == 'BENIGNTRAFFIC': return 'Normal'
    
    if 'DDOS' in label:
        if 'TCP' in label or 'SYN' in label or 'HTTP' in label:
            return 'DDoS-TCP'
        else:
            return 'DDoS-UDP/ICMP'
            
    if 'DOS' in label:
        if 'TCP' in label or 'SYN' in label or 'HTTP' in label:
            return 'DoS-TCP'
        else:
            return 'DoS-UDP/ICMP'

    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    if 'WEB' in label: return 'Web-Attack'
    
    return 'Outros'

df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

print("3. A preparar dados para o XGBoost...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])
joblib.dump(le, 'label_encoder_categorias_xgb.pkl')

y = df['label_encoded']
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1)

# --- FILTRO DE PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. TREINO ---
print("4. A dividir Treino (80%) / Teste (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. A treinar o Modelo XGBoost (Multi-Classe)...")
# ATENÇÃO: Mudámos para o XGBClassifier.
# n_jobs=-1 continua a ser usado para acelerar usando todos os núcleos do CPU.
# O XGBoost lida super bem com multi-classe automaticamente.
modelo = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
modelo.fit(X_train, y_train)

# --- 5. GUARDAR ---
print("6. A guardar o cérebro da IA...")
joblib.dump(modelo, 'modelo_ciberseguranca_xgb.pkl')
print("Ficheiro 'modelo_ciberseguranca_xgb.pkl' guardado com sucesso.")
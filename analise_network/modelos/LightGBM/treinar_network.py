import pandas as pd
import numpy as np
import lightgbm as lgb # <--- MUDANÇA: Importar LightGBM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import gc

# --- CONFIGURAÇÃO ---
# 1. MUDANÇA: Agora só carregamos o ficheiro levezinho e balanceado!
caminho_dataset = '../../datasets/dataset_treino.csv' 

print("🚀 A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (LIGHTGBM PURO E LEVE)...")
print("1. A carregar dataset balanceado (vai ser super rápido!)...")

try:
    df = pd.read_csv(caminho_dataset, low_memory=False)
    print(f"✅ Dados carregados! Pacotes analisados: {len(df)}")
except FileNotFoundError:
    print("❌ ERRO: Não encontrei o ficheiro csv balanceado.")
    print(f"Verifica se o caminho '{caminho_dataset}' está correto.")
    exit()

# --- 2. ENGENHARIA DE FEATURES ---
print("2. A organizar labels...")

# Como o nosso script de extração já criou a coluna 'categoria', 
# usamos este 'if' para evitar refazer o trabalho (poupa tempo!)
def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    if label == 'BENIGNTRAFFIC' or label == 'BENIGN': return 'Normal'
    if 'DDOS' in label: return 'DDoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DDoS-UDP/ICMP'
    if 'DOS' in label: return 'DoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DoS-UDP/ICMP'
    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    # if 'WEB' in label: return 'Web-Attack'
    return 'Outros'
df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

print("3. A preparar dados para o LightGBM...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])
# MUDANÇA: Guardar com nome específico para o LGBM
joblib.dump(le, 'label_encoder_categorias_lgbm.pkl')

y = df['label_encoded']
# Deitamos fora colunas de texto com errors='ignore' para evitar paragens no código
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1, errors='ignore')

# --- FIL মাস্টার PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. TREINO ---
print("4. A dividir Treino (80%) / Teste (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. A treinar o Modelo LightGBM (Multi-Classe, Naturalmente Balanceado)...")

# 2. MUDANÇA: Chamar o classificador do LightGBM
modelo = lgb.LGBMClassifier(n_estimators=100, random_state=42, n_jobs=-1)

# 3. MUDANÇA: O fit() direto e limpo!
modelo.fit(X_train, y_train)

# --- 5. GUARDAR ---
print("6. A guardar o cérebro da IA...")
# MUDANÇA: Guardar com o nome certo
joblib.dump(modelo, 'modelo_ciberseguranca_lgbm.pkl')
print("✅ Ficheiro 'modelo_ciberseguranca_lgbm.pkl' guardado com sucesso.")
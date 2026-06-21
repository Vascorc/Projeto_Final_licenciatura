import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# --- CONFIGURAÇÃO ---
# 1. MUDANÇA: Usar apenas o dataset reduzido e balanceado!
caminho_dataset = '../../datasets/dataset_treino.csv' 

print("🚀 A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (RANDOM FOREST PURO)...")
print("1. A carregar dataset balanceado (vai ser super rápido!)...")

try:
    df = pd.read_csv(caminho_dataset, low_memory=False)
    print(f"✅ Dados carregados! Pacotes analisados: {len(df)}")
except FileNotFoundError:
    print("❌ ERRO: Não encontrei o ficheiro csv.")
    print(f"Verifica se o caminho '{caminho_dataset}' está correto.")
    exit()

# --- 2. ENGENHARIA DE FEATURES ---
print("2. A organizar labels...")

# Se a coluna 'categoria' por acaso não estiver no CSV, nós recriamo-la para segurança
if 'categoria' not in df.columns:
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

print("   -> Distribuição das Categorias de Ataque:")
print(df['categoria'].value_counts())

print("3. A preparar dados para o Random Forest...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])

# Guardamos o codificador para uso futuro
joblib.dump(le, 'label_encoder_categorias_rf.pkl')

y = df['label_encoded']
# Deitamos fora as colunas de texto (Label e categoria) para o modelo funcionar com matemática
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1, errors='ignore')

# --- FILTRO DE PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. TREINO ---
print("4. A dividir Treino (80%) / Teste (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. A treinar o Modelo Random Forest (Multi-Classe, Naturalmente Balanceado)...")
# 2. MUDANÇA: O parâmetro class_weight='balanced' foi removido!
modelo = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
modelo.fit(X_train, y_train)

# --- 5. GUARDAR ---
print("6. A guardar o cérebro da IA...")
joblib.dump(modelo, 'modelo_ciberseguranca_rf.pkl')
print("✅ Ficheiro 'modelo_ciberseguranca_rf.pkl' guardado com sucesso.")
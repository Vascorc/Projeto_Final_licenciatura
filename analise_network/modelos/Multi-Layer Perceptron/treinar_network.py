import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neural_network import MLPClassifier
import joblib
import gc

# --- CONFIGURAÇÃO ---
caminho_dataset1 = '../../datasets/Merged01.csv' 
caminho_dataset2 = '../../datasets/Merged02.csv' 

print("🧠 A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (REDE NEURONAL - MLP)...")
print("1. A carregar datasets CICIoT2023 (isto pode demorar)...")

try:
    df1 = pd.read_csv(caminho_dataset1, low_memory=False)
    df2 = pd.read_csv(caminho_dataset2, low_memory=False)
    
    print("   -> A fundir os ficheiros...")
    df = pd.concat([df1, df2], ignore_index=True)
    
    del df1, df2
    gc.collect()
    
    print(f"✅ Dados carregados! pacotes analisados: {len(df)}")

except FileNotFoundError:
    print("❌ ERRO: Não encontrei os ficheiros csv.")
    exit()

# --- 2. ENGENHARIA DE FEATURES ---
print("2. A aplicar Lógica de Mitigação Inteligente...")

def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    
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

print("3. A preparar dados e labels...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])
joblib.dump(le, 'label_encoder_categorias_mlp.pkl')

y = df['label_encoded']
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1)

# --- FILTRO DE PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. DIVISÃO E SCALING (A GRANDE DIFERENÇA!) ---
print("4. A dividir Treino (80%) / Teste (20%)...")
# A divisão tem de ser feita ANTES do scaling por rigor estatístico (evitar data leakage)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("   -> A esmagar os dados para a mesma escala (StandardScaler)...")
scaler = StandardScaler()

# Aprendemos a escala apenas com os dados de treino e transformamos logo
X_train_escalado = scaler.fit_transform(X_train)

# Guardamos o Scaler! É a nossa "Fita Métrica" para o Router usar mais tarde
joblib.dump(scaler, 'scaler_ciberseguranca_mlp.pkl')
print("   ✅ Scaler guardado com sucesso!")

# --- 5. TREINO ---
print("5. A treinar a Rede Neuronal (MLP)...")
print("⏳ AVISO: Redes Neuronais exigem muita matemática. Isto pode demorar vários minutos!")

# hidden_layer_sizes=(50,) -> 1 camada oculta com 50 neurónios. early_stopping=True previne demoras eternas.
modelo = MLPClassifier(hidden_layer_sizes=(50,), max_iter=100, random_state=42, early_stopping=True)

# O MLP recebe os dados ESCALADOS. (Não usamos sample_weight aqui porque o sklearn não suporta no MLP)
modelo.fit(X_train_escalado, y_train)

# --- 6. GUARDAR ---
print("6. A guardar o cérebro da IA...")
joblib.dump(modelo, 'modelo_ciberseguranca_mlp.pkl')
print("Ficheiro 'modelo_ciberseguranca_mlp.pkl' guardado com sucesso.")
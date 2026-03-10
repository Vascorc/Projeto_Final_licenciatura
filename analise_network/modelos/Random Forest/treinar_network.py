import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import gc # Garbage Collector para libertar RAM

# --- CONFIGURAÇÃO ---
caminho_dataset1 = '../../datasets/Merged01.csv' 
caminho_dataset2 = '../../datasets/Merged02.csv' 

print("A INICIAR SISTEMA DE TREINO DE CIBERSEGURANÇA (RANDOM FOREST)...")
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
    print("Verifica se o caminho '../../datasets/Merged01.csv' está correto.")
    exit()

# --- 2. ENGENHARIA DE FEATURES (AGRUPAMENTO POR MITIGAÇÃO) ---
print("2. A aplicar Lógica de Mitigação Inteligente...")

def categorizar_ataque_mitigacao(label):
    label = str(label)
    
    if label == 'BENIGNTRAFFIC': return 'Normal'
    
    if 'DDOS' in label:
        if 'TCP' in label or 'SYN' in label or 'HTTP' in label:
            return 'DDOS-TCP'
        else:
            return 'DDOS-UDP/ICMP'
            
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

print("   -> Distribuição das Categorias de Ataque:")
print(df['categoria'].value_counts())

print("3. A preparar dados para o Random Forest...")

le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])

# Guardamos o codificador para uso futuro
joblib.dump(le, 'label_encoder_categorias_rf.pkl')

y = df['label_encoded']
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1)

# --- FILTRO DE PUREZA UNIVERSAL ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 4. TREINO ---
print("4. A dividir Treino (80%) / Teste (20%)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("5. A treinar o Modelo Random Forest (Multi-Classe)...")
# Mudamos de Regressor (números) para Classifier (categorias)
# O parâmetro n_jobs=-1 é crucial aqui para usar todos os núcleos do CPU
modelo = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
modelo.fit(X_train, y_train)

# --- 5. GUARDAR ---
print("6. A guardar o cérebro da IA...")
joblib.dump(modelo, 'modelo_ciberseguranca_rf.pkl')
print("Ficheiro 'modelo_ciberseguranca_rf.pkl' guardado com sucesso.")
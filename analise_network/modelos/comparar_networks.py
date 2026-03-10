import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
import gc

# --- 1. CARREGAR DADOS ---
print("A iniciar Avaliação Global de Cibersegurança...")
print("A carregar ficheiros CICIoT2023...")

try:
    df1 = pd.read_csv('../datasets/Merged01.csv', low_memory=False)
    df2 = pd.read_csv('../datasets/Merged02.csv', low_memory=False)
    df = pd.concat([df1, df2], ignore_index=True)
    del df1, df2
    gc.collect()
except FileNotFoundError:
    print("ERRO: Ficheiros CSV não encontrados.")
    exit()

# --- 2. ENGENHARIA DE FEATURES ---
print("A recriar o ambiente de teste exato...")

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

# Aplicar categorização
df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

# Transformar categorias em números
le = LabelEncoder()
df['label_encoded'] = le.fit_transform(df['categoria'])

# Extrair X e y
y = df['label_encoded']
X = df.drop(['Label', 'label_encoded', 'categoria'], axis=1)

# --- FILTRO DE PUREZA UNIVERSAL (Agora no sítio certo!) ---
print("   -> A limpar valores infinitos ou gigantes (Filtro Numpy)...")
X.replace([np.inf, -np.inf], np.nan, inplace=True)
X.fillna(0, inplace=True)

# --- 3. DIVISÃO E LIMPEZA DE MEMÓRIA ---
# Divisão exata graças ao random_state=42. Como o X já foi limpo, o X_test nasce limpo!
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Libertar a parte de treino da memória RAM, pois só vamos usar o X_test para avaliar
del X_train, y_train
gc.collect()

# --- 4. CARREGAR MODELOS TREINADOS ---
print("A carregar os modelos treinados...")
modelos = {
    'LightGBM': joblib.load('./LightGBM/modelo_ciberseguranca_LGBM.pkl'), 
    'Random Forest': joblib.load('./Random Forest/modelo_ciberseguranca_rf.pkl'),
    'XGBoost': joblib.load('./XGBoost/modelo_ciberseguranca_xgb.pkl')
}

resultados_acc = []
resultados_f1 = []
nomes = list(modelos.keys())

# --- 5. AVALIAR MODELOS ---
print("A gerar previsões e a calcular métricas...")
for nome, modelo in modelos.items():
    print(f" -> A testar {nome}...")
    previsoes = modelo.predict(X_test)
    
    acc = accuracy_score(y_test, previsoes)
    f1 = f1_score(y_test, previsoes, average='weighted')
    
    resultados_acc.append(acc * 100) # Converter para percentagem
    resultados_f1.append(f1 * 100)   # Converter para percentagem
    print(f"    [{nome}] Accuracy: {acc*100:.2f}% | F1-Score: {f1*100:.2f}%")

# --- 6. GERAR GRÁFICOS ---
print("A desenhar os gráficos...")
# Estilo profissional
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Comparação de Modelos - Deteção de Ciberataques (Edge IoT)', fontsize=16, fontweight='bold', color='#2C3E50')

# Cores: LightGBM (Azul), Random Forest (Verde), XGBoost (Vermelho/Laranja)
cores = ['#3498DB', '#2ECC71', '#E67E22']

# Gráfico 1: Accuracy
ax1.bar(nomes, resultados_acc, color=cores, edgecolor='black', alpha=0.8)
ax1.set_title('Accuracy Global (%) ↑', fontsize=14, pad=15)
ax1.set_ylabel('Percentagem', fontsize=12)
ax1.set_ylim(min(resultados_acc) - 1, 100.5) # Ajusta a escala para destacar a diferença
for i, v in enumerate(resultados_acc):
    ax1.text(i, v + 0.1, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=11)

# Gráfico 2: F1-Score
ax2.bar(nomes, resultados_f1, color=cores, edgecolor='black', alpha=0.8)
ax2.set_title('F1-Score Ponderado (%) ↑', fontsize=14, pad=15)
ax2.set_ylabel('Percentagem', fontsize=12)
ax2.set_ylim(min(resultados_f1) - 1, 100.5)
for i, v in enumerate(resultados_f1):
    ax2.text(i, v + 0.1, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('grafico_comparacao_ciberseguranca.png', dpi=300, bbox_inches='tight')
print("\nGráfico guardado com sucesso como 'grafico_comparacao_ciberseguranca.png'")
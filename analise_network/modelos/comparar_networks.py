import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, classification_report
import gc

# CARREGAR OS DADOS DO "MUNDO REAL" 
print("🚀 A iniciar a Avaliação Zero-Day (Teste Cego)...")
print("1. A carregar ficheiros de Validação...")

try:
    # Lê os ficheiros do 06 ao 10 ou ajusta o caminho para o teu novo ficheiro de validação
    df = pd.read_csv('../datasets/dataset_validar_treino.csv', low_memory=False)
    print(f"✅ Oceano de dados carregado! Total de pacotes a testar: {len(df)}")
except FileNotFoundError:
    print("❌ ERRO: Ficheiro de validação não encontrado.")
    exit()

# ENGENHARIA DE FEATURES
print("2. A aplicar a Lógica de Mitigação do Edge Router...")

def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    
    # CORREÇÃO 1: Voltar a meter a rede à prova de bala para tráfego legítimo
    if 'BENIGN' in label or 'NORMAL' in label: return 'Normal'
    
    if 'DDOS' in label: return 'DDoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DDoS-UDP/ICMP'
    if 'DOS' in label: return 'DoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DoS-UDP/ICMP'
    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    return 'Outros'

# Se a coluna 'categoria' já existir no teu dataset de validação, podes saltar esta linha
if 'Label' in df.columns:
    df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

print("3. A traduzir as categorias com o Dicionário Original...")
le = joblib.load('./XGBoost/label_encoder_categorias_xgb.pkl')
df['label_encoded'] = le.transform(df['categoria'])
nomes_das_classes = le.classes_ 

# --- 3. CARREGAR MODELOS E SCALER ---
print("4. A carregar os cérebros da IA treinados com o Super Dataset...")
modelos = {
    'LightGBM': joblib.load('./LightGBM/modelo_ciberseguranca_lgbm.pkl'), 
    'Random Forest': joblib.load('./Random Forest/modelo_ciberseguranca_rf.pkl'),
    'XGBoost': joblib.load('./XGBoost/modelo_ciberseguranca_xgb.pkl'),
    'Rede Neuronal (MLP)': joblib.load('./Multi-Layer_Perceptron/modelo_ciberseguranca_mlp.pkl')
}

scaler_mlp = joblib.load('./Multi-Layer_Perceptron/scaler_ciberseguranca_mlp.pkl')

# Extrair X e y 
y_test = df['label_encoded']
X_test = df.drop(['Label', 'label_encoded', 'categoria'], axis=1, errors='ignore')

X_test.columns = X_test.columns.str.replace(' ', '_')

# --- FILTRO DE PUREZA ---
print("   -> A limpar pacotes corrompidos...")
X_test.replace([np.inf, -np.inf], np.nan, inplace=True)
X_test.fillna(0, inplace=True)

# CORREÇÃO 2: Garantir que as colunas de teste são EXATAMENTE as mesmas do modelo treinado
modelo_referencia = modelos['LightGBM']
if hasattr(modelo_referencia, 'feature_name_'):
    features_esperadas = modelo_referencia.feature_name_
elif hasattr(modelo_referencia, 'feature_names_in_'):
    features_esperadas = modelo_referencia.feature_names_in_

# Reordenar colunas e descartar qualquer "lixo" que não tenha sido treinado
X_test = X_test[features_esperadas]

resultados_acc = []
resultados_f1 = []
nomes_modelos = list(modelos.keys())
acertos_por_anomalia = {classe: [] for classe in nomes_das_classes}

# --- 4. O BOMBARDEAMENTO DE TESTES ---
print("\n INÍCIO DO TESTE DE ESFORÇO (RESULTADOS POR ANOMALIA):\n" + "="*50)

for nome_modelo, modelo in modelos.items():
    print(f"\n A disparar contra o {nome_modelo}...")
    
    # Criar uma cópia fresca dos dados para este modelo
    X_teste_atual = X_test.copy()
    
    # O CAMALEÃO PARA O MODELO
    if hasattr(modelo, 'feature_names_in_'):
        X_teste_atual.columns = modelo.feature_names_in_
    elif hasattr(modelo, 'feature_name_'):
        X_teste_atual.columns = modelo.feature_name_
        
    # O Truque do MLP (E do seu Scaler)
    if nome_modelo == 'Rede Neuronal (MLP)':
        print("   -> A normalizar os pacotes (StandardScaler)...")
        # O Scaler também é exigente com os espaços, vamos dar-lhe o que ele quer!
        if hasattr(scaler_mlp, 'feature_names_in_'):
            X_teste_atual.columns = scaler_mlp.feature_names_in_
            
        X_teste_atual = scaler_mlp.transform(X_teste_atual)
        
    # A Previsão
    previsoes = modelo.predict(X_teste_atual)
    
    # Cálculos Globais
    acc = accuracy_score(y_test, previsoes)
    f1 = f1_score(y_test, previsoes, average='weighted')
    resultados_acc.append(acc * 100) 
    resultados_f1.append(f1 * 100)   
    
    # Cálculos por Classe (Recall)
    report = classification_report(y_test, previsoes, target_names=nomes_das_classes, output_dict=True, zero_division=0)
    
    for classe in nomes_das_classes:
        taxa_acerto = report[classe]['recall'] * 100 
        acertos_por_anomalia[classe].append(taxa_acerto)
        print(f"   -> {classe}: {taxa_acerto:.2f}% de acertos")
        
print("\n" + "="*50)

# GERAR GRÁFICOS
print("5. A revelar as fotografias finais do Teste Zero-Day...")
plt.style.use('seaborn-v0_8-whitegrid')
cores = ['#3498DB', '#2ECC71', '#E67E22', '#9B59B6'] 

# GRÁFICO 1: GLOBAIS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Métricas Globais (Teste Cego - Mundo Real)', fontsize=20, fontweight='bold')

ax1.bar(nomes_modelos, resultados_acc, color=cores, edgecolor='black', alpha=0.8)
ax1.set_title('Accuracy Global (%) ↑', fontsize=16, pad=15)
ax1.set_ylim(min(resultados_acc) - 1 if min(resultados_acc) > 1 else 0, 100.5)
ax1.tick_params(axis='x', labelsize=14)
ax1.tick_params(axis='y', labelsize=12)
for i, v in enumerate(resultados_acc):
    ax1.text(i, v + 0.1, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=13)

ax2.bar(nomes_modelos, resultados_f1, color=cores, edgecolor='black', alpha=0.8)
ax2.set_title('F1-Score Ponderado (%) ↑', fontsize=16, pad=15)
ax2.set_ylim(min(resultados_f1) - 1 if min(resultados_f1) > 1 else 0, 100.5)
ax2.tick_params(axis='x', labelsize=14)
ax2.tick_params(axis='y', labelsize=12)
for i, v in enumerate(resultados_f1):
    ax2.text(i, v + 0.1, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=13)

plt.tight_layout()
plt.savefig('grafico_teste_cego_global.png', dpi=300, bbox_inches='tight')

# GRÁFICO 2: POR ANOMALIA
fig2, ax3 = plt.subplots(figsize=(18, 8))
fig2.suptitle('Taxa de Acertos no Teste Cego (Recall %)', fontsize=20, fontweight='bold')

x = np.arange(len(nomes_das_classes)) 
largura_barra = 0.20

for i, nome_modelo in enumerate(nomes_modelos):
    valores_modelo = [acertos_por_anomalia[classe][i] for classe in nomes_das_classes]
    posicao = x + (i * largura_barra) - (largura_barra * 1.5)
    ax3.bar(posicao, valores_modelo, largura_barra, label=nome_modelo, color=cores[i], edgecolor='black', alpha=0.8)

ax3.set_xticks(x)
ax3.set_xticklabels(nomes_das_classes, rotation=45, ha='right', fontsize=14, fontweight='bold')
ax3.tick_params(axis='y', labelsize=12)
ax3.set_ylabel('Percentagem de Acertos (%)', fontsize=16)
ax3.set_ylim(0, 105)
ax3.legend(fontsize=14, loc='lower right')

ax3.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='Meta 90%')

plt.tight_layout()
plt.savefig('grafico_teste_cego_anomalias.png', dpi=300, bbox_inches='tight')

print("-----------------Gráficos do Teste Cego gerados com sucesso!-----------------")
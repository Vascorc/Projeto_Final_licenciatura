import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, classification_report
import gc

# CARREGAR OS DADOS DO "MUNDO REAL" 
print("🚀 A iniciar a Avaliação (Foco em Categorias Específicas)...")
print("1. A carregar ficheiros de Validação...")

try:
    # Ajusta o caminho para o teu novo ficheiro de validação
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

if 'Label' in df.columns:
    df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

print("3. A traduzir as categorias com o Dicionário Original...")
le = joblib.load('./XGBoost/label_encoder_categorias_xgb.pkl')
df['label_encoded'] = le.transform(df['categoria'])
nomes_das_classes = le.classes_ 

# --- 3. CARREGAR MODELOS E SCALER ---
print("4. A carregar os modelos treinados...")
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

nomes_modelos = list(modelos.keys())
acertos_por_anomalia = {classe: [] for classe in nomes_das_classes}

# --- 4. O BOMBARDEAMENTO DE TESTES ---
print("\n INÍCIO DO TESTE DE ESFORÇO:\n" + "="*50)

for nome_modelo, modelo in modelos.items():
    print(f"\n A analisar com o {nome_modelo}...")
    
    X_teste_atual = X_test.copy()
    
    if hasattr(modelo, 'feature_names_in_'):
        X_teste_atual.columns = modelo.feature_names_in_
    elif hasattr(modelo, 'feature_name_'):
        X_teste_atual.columns = modelo.feature_name_
        
    if nome_modelo == 'Rede Neuronal (MLP)':
        if hasattr(scaler_mlp, 'feature_names_in_'):
            X_teste_atual.columns = scaler_mlp.feature_names_in_
        X_teste_atual = scaler_mlp.transform(X_teste_atual)
        
    previsoes = modelo.predict(X_teste_atual)
    
    report = classification_report(y_test, previsoes, target_names=nomes_das_classes, output_dict=True, zero_division=0)
    
    for classe in nomes_das_classes:
        taxa_acerto = report[classe]['recall'] * 100 
        acertos_por_anomalia[classe].append(taxa_acerto)
        
print("\n" + "="*50)

# GERAR GRÁFICOS ESPECÍFICOS
print("5. A gerar gráficos específicos em formato 4x4 (Normal, BruteForce, Recon)...")
plt.style.use('seaborn-v0_8-whitegrid')
cores = ['#3498DB', '#2ECC71', '#E67E22', '#9B59B6'] 
nomes_curtos = ['LightGBM', 'RF', 'XGBoost', 'MLP']

categorias_alvo = ['Normal', 'BruteForce', 'Recon']

for categoria in categorias_alvo:
    if categoria not in nomes_das_classes:
        print(f"Aviso: Categoria {categoria} não encontrada no dicionário original!")
        continue
        
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.suptitle(f'Taxa de Acertos - {categoria}', fontsize=12, fontweight='bold')
    
    valores = [acertos_por_anomalia[categoria][i] for i in range(len(nomes_modelos))]
    
    barras = ax.bar(nomes_curtos, valores, color=cores, edgecolor='black', alpha=0.8, width=0.6)
    
    ax.set_ylabel('Acertos (%)', fontsize=10)
    ax.set_ylim(0, 105)
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', labelsize=8)
    
    # Adicionar os valores em cima das barras
    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2., altura + 1.5,
                f'{altura:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
                
    if categoria == 'Normal':
        ax.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='Meta 90%')
    else:
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Meta 80%')
        
    ax.legend(fontsize=8, loc='lower right')
    
    plt.tight_layout()
    nome_ficheiro = f'grafico_teste_cego_{categoria.lower()}.png'
    plt.savefig(nome_ficheiro, dpi=300, bbox_inches='tight')
    print(f"   -> Gráfico gravado: {nome_ficheiro}")
    plt.close()

print("-----------------Gráficos Específicos gerados com sucesso!-----------------")

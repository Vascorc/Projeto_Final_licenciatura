#----------------------------------------------------------------------------
#Este ficheiro apenas treina o modelo com o dataset reduzido de Merged01.csv
#é testado tanto com dataset usado para treinar como o de ambiente industrial
#----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Configuração visual
sns.set_style("whitegrid")

# ==========================================
# FASE 1: TREINO NO AMBIENTE DOMÉSTICO (CIC)
# ==========================================
print("\n=== FASE 1: TREINO NO AMBIENTE DOMÉSTICO (CIC) ===")

# 1. CARREGAR O DATASET CIC
caminho_cic = os.path.join('..', 'datasets', 'dataset_tratado.csv')
if not os.path.exists(caminho_cic):
    print("❌ ERRO: dataset_tratado.csv não encontrado.")
    sys.exit()

df = pd.read_csv(caminho_cic)

# 2. EQUILIBRAR CLASSES (Reduzir DDoS)
df_ddos = df[df['classe_final'] == 'DDoS']
df_outros = df[df['classe_final'] != 'DDoS']
df_ddos_reduzido = df_ddos.sample(n=20000, random_state=42)
df_final = pd.concat([df_ddos_reduzido, df_outros]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Dataset de Treino Equilibrado: {len(df_final)} linhas")

# 3. PREPARAR DADOS
y = df_final['classe_final']
X = df_final.drop(columns=['classe_final', 'label', 'Label'], errors='ignore')

# Guardar nomes das classes
y_cat = y.astype('category')
nomes_classes = y_cat.cat.categories.tolist() # ['DDoS', 'Injection', 'Normal', 'Scanning']
print(f"Classes: {nomes_classes}")

# Dividir Treino/Teste
X_train, X_test_cic, y_train, y_test_cic = train_test_split(X, y_cat.cat.codes, test_size=0.2, random_state=42)

# 4. TREINAR MODELO
print("--- A Treinar LightGBM... ---")
modelo = lgb.LGBMClassifier(random_state=42)
modelo.fit(X_train, y_train)

# 5. AVALIAR NO CIC (DOMÉSTICO)
preds_cic = modelo.predict(X_test_cic)
acc_cic = accuracy_score(y_test_cic, preds_cic)
print(f"🏆 Acurácia Doméstica: {acc_cic:.2%}")

# GRÁFICO 1: SUCESSO DOMÉSTICO
plt.figure(figsize=(10, 8))
sns.heatmap(confusion_matrix(y_test_cic, preds_cic), annot=True, fmt='d', cmap='Greens', 
            xticklabels=nomes_classes, yticklabels=nomes_classes)
plt.title(f'Cenário 1: Teste em Ambiente Conhecido (Doméstico)\nAcurácia: {acc_cic:.1%}')
plt.savefig(os.path.join('..','graficos','primeiro_modelo', '1_performance_domestica.png'))
print("✅ Gráfico 1 salvo: 1_performance_domestica.png")


# ==========================================
# FASE 2: O TESTE DE FOGO (INDUSTRIAL - TON_IoT)
# ==========================================
print("\n=== FASE 2: TESTE NO AMBIENTE INDUSTRIAL (TON_IoT) ===")

# 1. CARREGAR TON_IOT
caminho_ton = os.path.join('..', 'datasets', 'TON_Iot_Train_Test_Network.csv')
if not os.path.exists(caminho_ton):
    print("❌ ERRO: TON_Iot_Train_Test_Network.csv não encontrado. (O teste industrial vai falhar)")
    sys.exit()

# Ler e limpar
df_ton = pd.read_csv(caminho_ton, na_values=['-', 'nan'], low_memory=False)
colunas_num = ['duration', 'src_pkts', 'dst_pkts', 'src_bytes']
for col in colunas_num:
    df_ton[col] = pd.to_numeric(df_ton[col], errors='coerce').fillna(0)

# 2. HARMONIZAR COLUNAS (Fazer o TON parecer-se com o CIC)
df_teste_ind = pd.DataFrame()

# Mapeamento
duracao = df_ton['duration'].replace(0, 0.001)
df_teste_ind['flow_duration'] = df_ton['duration']
df_teste_ind['Rate'] = (df_ton['src_pkts'] + df_ton['dst_pkts']) / duracao
df_teste_ind['Srate'] = df_ton['src_pkts'] / duracao
df_teste_ind['Drate'] = df_ton['dst_pkts'] / duracao
df_teste_ind['Protocol Type'] = df_ton['proto'].astype(str).str.lower().map({'tcp': 6, 'udp': 17, 'icmp': 1}).fillna(0)

# Colunas que faltam (Flags, etc) enchemos com 0
for col in X.columns:
    if col not in df_teste_ind.columns:
        df_teste_ind[col] = 0
        
# Garantir ordem das colunas
X_test_ind = df_teste_ind[X.columns]

# 3. PREPARAR AS CLASSES REAIS DO TON
def normalizar_ton(label):
    label = str(label).lower()
    if 'normal' in label: return 2     # Normal
    if 'dos' in label or 'ddos' in label: return 0 # DDoS
    if 'scan' in label or 'recon' in label: return 3 # Scanning
    return 1 # Injection / Outros

y_test_ind = df_ton['type'].apply(normalizar_ton)

# 4. PREVER COM O MODELO DOMÉSTICO
preds_ind = modelo.predict(X_test_ind)
acc_ind = accuracy_score(y_test_ind, preds_ind)
print(f"⚠️ Acurácia Industrial: {acc_ind:.2%}")

# GRÁFICO 2: O FRACASSO INDUSTRIAL
plt.figure(figsize=(10, 8))
sns.heatmap(confusion_matrix(y_test_ind, preds_ind), annot=True, fmt='d', cmap='Reds', 
            xticklabels=nomes_classes, yticklabels=nomes_classes)
plt.title(f'Cenário 2: Teste em Ambiente Desconhecido (Industrial)\nAcurácia: {acc_ind:.1%}')
plt.xlabel('O que o Modelo "Doméstico" achou que era')
plt.ylabel('A Realidade Industrial')
plt.savefig(os.path.join('..','graficos','primeiro_modelo', '2_performance_industrial.png'))
print("✅ Gráfico 2 salvo: 2_performance_industrial.png")

# Salvar modelo
modelo.booster_.save_model(os.path.join('..', 'modelo_iot.txt'))
print("\n💾 Modelo Base Salvo.")
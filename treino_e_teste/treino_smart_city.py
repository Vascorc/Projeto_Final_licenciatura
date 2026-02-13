#----------------------------------------------------------------------------
#Este ficheiro apenas treina o modelo com o dataset reduzido de Merged01.csv
#e com o dataset TON_IoT_Train_Test.csv
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

# 1. CARREGAR O DATASET TRATADO
print("--- 1. A CARREGAR DADOS ---")
caminho_csv = os.path.join('..', 'datasets', 'dataset_tratado.csv')

if not os.path.exists(caminho_csv):
    print(f"❌ ERRO: Não encontrei o ficheiro em {os.path.abspath(caminho_csv)}")
    sys.exit()

df = pd.read_csv(caminho_csv)

# 2. RESOLVER O DESEQUILÍBRIO (TÉCNICA MANUAL)
print("--- 2. A EQUILIBRAR CLASSES (Reduzindo DDoS) ---")

# Separar as classes
df_ddos = df[df['classe_final'] == 'DDoS']
df_normal = df[df['classe_final'] == 'Normal']
df_scanning = df[df['classe_final'] == 'Scanning']
df_injection = df[df['classe_final'] == 'Injection']

print(f"Contagem Original: DDoS={len(df_ddos)}, Normal={len(df_normal)}, Scanning={len(df_scanning)}, Injection={len(df_injection)}")

# Reduzir DDoS para 20.000 amostras (ou menos se não tiver 20k)
n_amostras = 20000
df_ddos_reduzido = df_ddos.sample(n=min(len(df_ddos), n_amostras), random_state=42)

# Juntar tudo de novo
df_final = pd.concat([df_ddos_reduzido, df_normal, df_scanning, df_injection])

# Baralhar as linhas
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Dataset Equilibrado Final: {len(df_final)} linhas")

# 3. PREPARAR PARA O TREINO
print("--- 3. A PREPARAR DADOS PARA O MODELO ---")

# Separar X e y
y = df_final['classe_final']
colunas_remover = ['classe_final', 'label', 'Label']
cols_to_drop = [c for c in colunas_remover if c in df_final.columns]
X = df_final.drop(columns=cols_to_drop)

# --- PASSO IMPORTANTE: GUARDAR OS NOMES DAS CLASSES ---
# O método .astype('category') organiza por ordem alfabética por defeito
y_cat = y.astype('category')
nomes_classes = y_cat.cat.categories.tolist() # Ex: ['DDoS', 'Injection', 'Normal', 'Scanning']
print(f"Ordem das Classes detetada: {nomes_classes}")

# Converter para números para o LightGBM treinar
y_encoded = y_cat.cat.codes

# Dividir Treino/Teste
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# 4. TREINAR O MODELO
print("\n--- 4. A TREINAR O LIGHTGBM ---")
# Aqui não precisamos de class_weight='balanced' porque já equilibraste manualmente acima!
modelo = lgb.LGBMClassifier(random_state=42)
modelo.fit(X_train, y_train)

# 5. AVALIAÇÃO E GRÁFICOS
print("\n--- 5. RESULTADOS E GRÁFICOS ---")
previsoes = modelo.predict(X_test)

acuracia = accuracy_score(y_test, previsoes)
print(f"🏆 Acurácia Global: {acuracia:.2%}")

# Gerar Matriz de Confusão
cm = confusion_matrix(y_test, previsoes)

# --- AQUI ESTÁ A PARTE DOS NOMES NO GRÁFICO ---
plt.figure(figsize=(10, 8))
sns.heatmap(cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues', 
            xticklabels=nomes_classes, # Mete os nomes em baixo
            yticklabels=nomes_classes) # Mete os nomes à esquerda

plt.title(f'Matriz de Confusão (Dataset Equilibrado)\nAcurácia: {acuracia:.2%}')
plt.ylabel('Realidade')
plt.xlabel('Previsão do Modelo')
plt.tight_layout()

# Salvar gráfico
nome_imagem = 'matriz_treino_equilibrado.png'
plt.savefig(nome_imagem, dpi=300)
print(f"✅ Gráfico com nomes salvo como: {nome_imagem}")

# 6. SALVAR O MODELO
caminho_modelo = os.path.join('..', 'modelo_iot_equilibrado.txt')
modelo.booster_.save_model(caminho_modelo)
print(f"\n💾 Modelo salvo em: {caminho_modelo}")
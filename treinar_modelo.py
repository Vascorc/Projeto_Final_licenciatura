import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. CARREGAR O DATASET TRATADO
print("--- A CARREGAR DADOS ---")
df = pd.read_csv(os.path.join('datasets', 'dataset_tratado.csv'))

# 2. RESOLVER O DESEQUILÍBRIO 
# separamos as classes
df_ddos = df[df['classe_final'] == 'DDoS']
df_normal = df[df['classe_final'] == 'Normal']
df_scanning = df[df['classe_final'] == 'Scanning']
df_injection = df[df['classe_final'] == 'Injection']

# Vamos reduzir o DDoS para 20.000 amostras (para não abafar os outros)
# random_state=42 garante que escolhemos sempre as mesmas 20k linhas (reprodutibilidade)
df_ddos_reduzido = df_ddos.sample(n=20000, random_state=42)

# Juntar tudo de novo num dataset equilibrado
df_final = pd.concat([df_ddos_reduzido, df_normal, df_scanning, df_injection])

# Misturar as linhas para não ficarem ordenadas por tipo
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n--- DATASET EQUILIBRADO ---")
print(df_final['classe_final'].value_counts())

# 3. PREPARAR PARA O TREINO
# Separar a Resposta (y) das Perguntas (X)
y = df_final['classe_final']
# Removemos a coluna da resposta e a coluna original 'label' (se existir)
colunas_para_remover = ['classe_final', 'label', 'Label']
# Apenas remove as que realmente existem no dataframe
cols_to_drop = [c for c in colunas_para_remover if c in df_final.columns]
X = df_final.drop(columns=cols_to_drop)

# O LightGBM precisa que as classes sejam números, não texto
# Vamos converter: Normal->0, DDoS->1, Scanning->2, Injection->3
y = y.astype('category').cat.codes

# Dividir: 80% para Treinar, 20% para Testar 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. TREINAR O MODELO
print("\n--- A TREINAR O LIGHTGBM ---")
modelo = lgb.LGBMClassifier(random_state=42)
modelo.fit(X_train, y_train)

# 5. AVALIAÇÃO
print("\n--- RESULTADOS DO EXAME (TESTE) ---")
previsoes = modelo.predict(X_test)

acuracia = accuracy_score(y_test, previsoes)
print(f"Acurácia Global: {acuracia:.4f} (Isto é: {acuracia*100:.2f}%)")

print("\n--- RELATÓRIO DETALHADO POR CLASSE ---")
# Precisamos de saber qual número corresponde a qual nome
mapa_classes = dict(enumerate(df_final['classe_final'].astype('category').cat.categories))
print(f"Legenda das Classes: {mapa_classes}")
print(classification_report(y_test, previsoes))

# 6. SALVAR O MODELO
modelo.booster_.save_model('modelo_iot_final.txt')
print("\nModelo salvo como 'modelo_iot_final.txt'.")
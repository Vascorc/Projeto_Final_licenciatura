import pandas as pd
import os
#------------
# contar quantos ataques de cada tipo temos no ficheiro
#------------
caminho_ficheiro = os.path.join('datasets', 'Merged01.csv')

print("A carregar o dataset... (isto pode demorar um pouco)")
# Lemos apenas as primeiras 100.000 linhas para ser rápido a testar
df = pd.read_csv(caminho_ficheiro) #, nrows=100000) 

print(f"Dataset carregado! Tamanho: {df.shape}")

print("\n--- TIPOS DE ATAQUE ENCONTRADOS (Coluna 'Label') ---")
print(df['Label'].value_counts())

print("\n--- VERIFICAÇÃO DE VALORES NULOS ---")
print(df.isnull().sum().sum())
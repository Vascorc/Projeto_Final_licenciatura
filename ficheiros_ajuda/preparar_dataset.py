#------------
# este ficheiro vai limpar o dataset e apenas usar tipos de ataques que queremos
# Normal, DDoS, Scanning, Injection
#------------

import pandas as pd
import numpy as np
import os

# O nome do teu ficheiro original
ARQUIVO_ENTRADA = os.path.join('datasets', 'Merged01.csv')
ARQUIVO_SAIDA = os.path.join('datasets', 'dataset_tratado.csv')

print("--- A CARREGAR DADOS ---")
df = pd.read_csv(ARQUIVO_ENTRADA)

# 1. Limpeza Básica
# Remover espaços nos nomes das colunas
df.columns = df.columns.str.strip()
# Remover as 22 linhas com erros (valores nulos)
df.dropna(inplace=True)

# 2. A Função de Agrupamento 
def agrupar_ataques(label):
    label = str(label).upper() # Garantir que está tudo em maiúsculas
    
    # CLASSE 1: NORMAL
    if 'BENIGN' in label:
        return 'Normal'
    
    # CLASSE 2: DDoS (Inclui DOS e MIRAI)
    elif 'DDOS' in label or 'DOS' in label or 'MIRAI' in label:
        return 'DDoS'
    
    # CLASSE 3: SCANNING (Reconhecimento)
    elif 'SCAN' in label or 'RECON' in label or 'BRUTEFORCE' in label:
        return 'Scanning'
    
    # CLASSE 4: INJECTION (Spoofing, XSS, SQL, Malware)
    elif 'SPOOF' in label or 'INJECTION' in label or 'XSS' in label or 'HIJACKING' in label or 'MALWARE' in label or 'UPLOADING' in label:
        return 'Injection'
    
    # Redes de segurança (se sobrar algo estranho)
    else:
        return 'Outros'

print("--- A AGRUPAR CLASSES ---")

nome_coluna_label = 'label' if 'label' in df.columns else 'Label'

df['classe_final'] = df[nome_coluna_label].apply(agrupar_ataques)

print("\n--- RESULTADO FINAL (4 CLASSES) ---")
print(df['classe_final'].value_counts())

# 3. Salvar o ficheiro limpo
# Para já, salvamos todas as colunas, mas com a nova coluna 'classe_final'
print(f"\n--- A SALVAR FICHEIRO: {ARQUIVO_SAIDA} ---")
df.to_csv(ARQUIVO_SAIDA, index=False)
print("Feito!")
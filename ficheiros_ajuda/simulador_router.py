import lightgbm as lgb
import pandas as pd
import numpy as np
import os

# 1. CARREGAR O CÉREBRO (MODELO)
print("--- A INICIAR SISTEMA DE DETEÇÃO IOT ---")
try:
    # Tenta carregar o modelo salvo. 
    modelo = lgb.Booster(model_file='modelo_iot_final.txt')
    print("Modelo carregado com sucesso!")
except:
    print("ERRO: Não encontrei o ficheiro 'modelo_iot_final.txt'. Corre o treino primeiro!")
    exit()

# 2. SIMULAR DADOS A CHEGAR (Do Dataset Original)
# Vamos ler o dataset tratado só para tirar de lá uns exemplos para testar
df = pd.read_csv(os.path.join('datasets', 'dataset_tratado.csv'))

# Vamos escolher 10 exemplos aleatórios para testar
amostras = df.sample(10)

# Separar a resposta real (para sabermos se ele acertou) dos dados
respostas_reais = amostras['classe_final']
dados_para_analise = amostras.drop(columns=['classe_final', 'label', 'Label'], errors='ignore')

# 3. O LOOP DE DETEÇÃO EM "TEMPO REAL"
print("\n--- A MONITORIZAR TRÁFEGO ---")
print(f"{'PREVISÃO':<15} | {'REALIDADE':<15} | {'AÇÃO DO ROUTER'}")
print("-" * 60)

# Fazer a previsão para as 10 amostras
previsoes = modelo.predict(dados_para_analise)

# 0: DDoS
# 1: Injection
# 2: Normal
# 3: Scanning
classes = ['DDoS', 'Injection', 'Normal', 'Scanning']

for i, pred_probs in enumerate(previsoes):
    # Descobrir qual a classe com maior probabilidade
    classe_vencedora_index = np.argmax(pred_probs)
    classe_detetada = classes[classe_vencedora_index]
    real = respostas_reais.iloc[i]
    
    # Decidir a Ação
    acao = ""
    if classe_detetada == "Normal":
        acao = "✅ Permitir"
    elif classe_detetada == "DDoS":
        acao = "⛔ BLOQUEAR IP"
    elif classe_detetada == "Scanning":
        acao = "⚠️ Alerta (Log)"
    else:
        acao = "🔥 ALERTA CRÍTICO"

    print(f"{classe_detetada:<15} | {real:<15} | {acao}")

print("\n--- FIM DA SIMULAÇÃO ---")
import socket
import pandas as pd
import json
import time
import random
import os

HOST = '127.0.0.1'
PORT = 5000

print("--- A CARREGAR DADOS PARA SIMULAÇÃO ---")
# Carregar o dataset tratado para tirar exemplos reais
df = pd.read_csv(os.path.join('..', 'datasets', 'dataset_tratado.csv'))

# Tirar uma amostra aleatória grande para enviar
amostra = df.sample(n=1000) 

print(f"Preparado para enviar {len(amostra)} pacotes de tráfego...")
time.sleep(2)

# Conectar ao Router
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
except:
    print("ERRO: O Router não está ligado! Corre o 'router_inteligente.py' primeiro.")
    exit()

print("🚀 A INICIAR ATAQUE/TRÁFEGO...")

for index, row in amostra.iterrows():
    # Separar o rótulo dos dados
    label_real = row['classe_final']
    # Converter os dados para lista (sem as colunas de texto)
    dados = row.drop(['classe_final', 'label', 'Label'], errors='ignore').tolist()
    
    # Criar o pacote
    pacote = {
        'dados': dados,
        'real': label_real
    }
    
    # Enviar
    mensagem = json.dumps(pacote)
    client_socket.send(mensagem.encode())
    
    # Simular velocidade variável da rede
    # Se for DDoS, mandamos muito rápido. Se for normal, mais devagar.
    delay = random.uniform(0.05, 0.5) 
    if label_real == 'DDoS':
        delay = 0.01 # Ataque rápido!
        
    time.sleep(delay)
    print(f"Enviado: {label_real}")

client_socket.close()
print("Simulação terminada.")
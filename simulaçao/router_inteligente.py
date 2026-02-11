import socket
import json
import lightgbm as lgb
import numpy as np
import time
import os

# CONFIGURAÇÕES DO SERVIDOR
HOST = '127.0.0.1'  # Localhost (o teu próprio PC)
PORT = 5000         # A porta onde o router está à escuta

# 1. CARREGAR O CÉREBRO
print("--- A INICIAR SISTEMA DE PROTEÇÃO (ROUTER) ---")
try:
    modelo = lgb.Booster(model_file=os.path.join('..', 'modelo_iot_final.txt'))
    print("Modelo IA carregado com sucesso!")
except:
    print("ERRO: Ficheiro 'modelo_iot_final.txt' não encontrado.")
    exit()

# 0: DDoS, 1: Injection, 2: Normal, 3: Scanning
CLASSES = ['DDoS', 'Injection', 'Normal', 'Scanning']

# 2. CRIAR O SOCKET (O ouvido do router)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Router à escuta em {HOST}:{PORT}...")
print("A aguardar tráfego IoT...")

conn, addr = server_socket.accept()
print(f"Ligação estabelecida com: {addr}")

# 3. LOOP DE PROCESSAMENTO EM TEMPO REAL
total_pacotes = 0
bloqueios = 0

try:
    while True:
        # Receber dados (pacotes de 4KB)
        data = conn.recv(4096)
        if not data:
            break
        
        # O dado vem em texto, convertemos para JSON
        pacote = json.loads(data.decode())
        
        features = pacote['dados']      # As colunas numéricas
        label_real = pacote['real']     # Só para nós sabermos se acertou (cheat)
        
        # --- A MAGIA DA IA ---
        inicio = time.time()
        
        # O modelo exige formato 2D, por isso usamos [features]
        previsao_probs = modelo.predict([features])
        classe_idx = np.argmax(previsao_probs)
        classe_detetada = CLASSES[classe_idx]
        
        tempo_processamento = (time.time() - inicio) * 1000 # em ms
        
        # --- LÓGICA DE MITIGAÇÃO ---
        acao = ""
        cor = ""
        
        if classe_detetada == "Normal":
            acao = "✅ PASSOU"
            cor = "\033[92m" # Verde
        elif classe_detetada == "DDoS":
            acao = "⛔ BLOQUEADO"
            cor = "\033[91m" # Vermelho
            bloqueios += 1
        elif classe_detetada == "Scanning":
            acao = "⚠️ ALERTA"
            cor = "\033[93m" # Amarelo
        else: # Injection
            acao = "🔥 CRÍTICO"
            cor = "\033[95m" # Roxo
            
        # Reset da cor
        fim_cor = "\033[0m"

        total_pacotes += 1
        
        # Imprimir Log Bonito
        print(f"Pacote #{total_pacotes} | {cor}{classe_detetada:<10}{fim_cor} | Real: {label_real:<10} | {acao} ({tempo_processamento:.2f}ms)")

except KeyboardInterrupt:
    print("\n--- SISTEMA PARADO PELO UTILIZADOR ---")
    print(f"Total Analisado: {total_pacotes}")
    print(f"Ameaças Bloqueadas: {bloqueios}")

conn.close()
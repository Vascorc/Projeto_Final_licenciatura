import socket
import csv
import time
import random

# 1. CONFIGURAÇÕES
IP_ALVO = "10.0.0.2" # IP do host h2 no Mininet
PORTA = 5005
FICHEIRO_CSV = "../analise_network/datasets/dataset_benigno.csv" 

# AJUSTE DE VELOCIDADE: 
# 0.005 = ~200 pacotes por segundo (Bom equilíbrio para o Scapy não perder pacotes)
ATRASO = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"🚀 Simulação: Enviando tráfego benigno de '{FICHEIRO_CSV}' para {IP_ALVO}...")

contador = 0
tempo_inicio = time.time()

try:
    with open(FICHEIRO_CSV, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Pula a linha do Header
        
        linhas_benignas = list(reader)
        
    # Baralhar aleatoriamente os pacotes benignos
    random.shuffle(linhas_benignas)
    
    for linha in linhas_benignas:
        dados_para_ia = linha[:-2] 
        mensagem = ",".join(dados_para_ia)
        sock.sendto(mensagem.encode(), (IP_ALVO, PORTA))
        
        contador += 1
        
        # Mostra o progresso apenas a cada 1000 pacotes para não abrandar o CPU!
        if contador % 1000 == 0:
            print(f"[PROGRESSO] {contador} pacotes benignos já disparados...")
        
        # Pausa milimétrica para a IA do outro lado ter tempo de processar
        if ATRASO > 0:
            time.sleep(ATRASO)
            
    tempo_fim = time.time()
    minutos = (tempo_fim - tempo_inicio) / 60
    print(f"\n✅ Simulação terminada! Foram enviados {contador} pacotes em {minutos:.2f} minutos.")
            
except FileNotFoundError:
    print(f"ERRO: O ficheiro '{FICHEIRO_CSV}' não existe!")
except Exception as e:
    print(f"Erro inesperado: {e}")

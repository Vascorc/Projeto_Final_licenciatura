import socket
import csv
import time

# 1. CONFIGURAÇÕES
IP_ALVO = "10.0.0.2" # IP do host h2 no Mininet
PORTA = 5005
FICHEIRO_CSV = "../../analise_network/datasets/dataset_validar_treino.csv" 

ATRASO = 0.015 # Velocidade ideal para a tua máquina estável

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"🚀 Simulação: Enviando dados com ID de '{FICHEIRO_CSV}' para {IP_ALVO}...")

contador = 0
tempo_inicio = time.time()

try:
    with open(FICHEIRO_CSV, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Pula a linha do Header
        
        # O id_original guarda o número exato da linha no CSV original!
        for id_original, linha in enumerate(reader):
            dados_para_ia = linha[:-2] 
            
            # Injetamos o id_original no início da mensagem separado por uma vírgula
            mensagem = f"{id_original}," + ",".join(dados_para_ia)
            sock.sendto(mensagem.encode(), (IP_ALVO, PORTA))
            
            contador += 1
            if contador % 1000 == 0:
                print(f"[PROGRESSO] {contador} ataques já disparados...")
            
            if ATRASO > 0:
                time.sleep(ATRASO)
                
    tempo_fim = time.time()
    minutos = (tempo_fim - tempo_inicio) / 60
    print(f"\n✅ Simulação terminada! Foram enviados {contador} pacotes em {minutos:.2f} minutos.")
            
except FileNotFoundError:
    print(f"ERRO: O ficheiro '{FICHEIRO_CSV}' não existe!")
except Exception as e:
    print(f"Erro inesperado: {e}")
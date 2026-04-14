import socket
import csv
import time

# 1. CONFIGURAÇÕES
IP_ALVO = "192.168.1.10"
PORTA = 5005
# AJUSTADO: Nome exato do teu ficheiro
FICHEIRO_CSV = "dataset_ataque.csv" 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"🚀 Simulação: Enviando dados de '{FICHEIRO_CSV}' para {IP_ALVO}...")

try:
    with open(FICHEIRO_CSV, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Pula a linha do Header (Header_Length, Protocol Type, etc.)
        
        for linha in reader:
            # O teu CSV tem 41 colunas:
            # - Colunas 0 a 38: Características (39 totais)
            # - Coluna 39: Label (DOS-TCP_FLOOD)
            # - Coluna 40: categoria (DoS-TCP)
            
            # Usamos [:-2] para enviar APENAS as primeiras 39 (até à 'Variance')
            dados_para_ia = linha[:-2] 
            
            mensagem = ",".join(dados_para_ia)
            sock.sendto(mensagem.encode(), (IP_ALVO, PORTA))
            
            print(f"📤 [SENT] {len(dados_para_ia)} features (Variance={dados_para_ia[-1]})")
            
            # Espera 1 segundo para não "afogar" o Ubuntu
            time.sleep(1)
            
except FileNotFoundError:
    print(f"❌ ERRO: O ficheiro '{FICHEIRO_CSV}' não existe no diretório /root do Kali!")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

print("🏁 Simulação terminada!")
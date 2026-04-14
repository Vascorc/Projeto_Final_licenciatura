import joblib
import os
import pandas as pd
import numpy as np
from scapy.all import sniff, IP

# --- 1. CONFIGURAÇÃO E CARREGAMENTO ---
print("🚀 A iniciar Sistema de Mitigação no Edge...")

# Caminhos corrigidos para minúsculas (padrão Linux)
CAMINHO_MODELO = './LightGBM/modelo_ciberseguranca_lgbm.pkl'
CAMINHO_ENCODER = './LightGBM/label_encoder_categorias_lgbm.pkl'

try:
    modelo = joblib.load(CAMINHO_MODELO)
    le = joblib.load(CAMINHO_ENCODER)
    print("✅ Inteligência Artificial carregada com sucesso!")
    print(f"📊 O modelo está à espera de {len(modelo.feature_name_)} características.")
except Exception as e:
    print(f"❌ Erro ao carregar modelos: {e}")
    exit()

# --- 2. FUNÇÃO DE EXECUÇÃO DE FIREWALL ---
def executar_comando(comando):
    print(f"🛠️ A executar: {comando}")
    # os.system(comando) # Descomenta quando quiseres que o bloqueio seja REAL

def aplicar_mitigacao(classe, ip_atacante):
    if classe in ['DDoS-TCP', 'DoS-TCP']:
        executar_comando(f"iptables -A INPUT -p tcp -s {ip_atacante} -j DROP")
    elif classe in ['DDoS-UDP/ICMP', 'DoS-UDP/ICMP']:
        executar_comando(f"iptables -A INPUT -p udp -s {ip_atacante} -j DROP")
        executar_comando(f"iptables -A INPUT -p icmp -s {ip_atacante} -j DROP")
    elif classe == 'Mirai-Botnet' or classe == 'Spoofing':
        executar_comando(f"iptables -A INPUT -s {ip_atacante} -j DROP")
    elif classe == 'BruteForce':
        executar_comando(f"iptables -A INPUT -p tcp --dport 22 -s {ip_atacante} -j REJECT")
    
    print(f"🛡️ Mitigação aplicada para: {classe} (IP: {ip_atacante})")

# --- 3. PROCESSAMENTO EM TEMPO REAL ---
def processar_pacote_em_tempo_real(dados_lista, ip_origem):
    # Convertemos a lista para DataFrame com os nomes que o modelo espera
    df_pacote = pd.DataFrame([dados_lista], columns=modelo.feature_name_)
    
    # Previsão
    previsao_num = modelo.predict(df_pacote)[0]
    classe_detetada = le.inverse_transform([previsao_num])[0]
    
    if classe_detetada != 'Normal':
        print(f"⚠️ ALERTA: {classe_detetada} detetado do IP {ip_origem}!")
        aplicar_mitigacao(classe_detetada, ip_origem)
    else:
        print(f"🟢 Tráfego Normal de {ip_origem}.")
 
# --- 4. MODO ESCUTA ---
def capturar_pacote(pacote):
    # 1. Verificamos se é um pacote IP e se traz dados UDP na porta 5005
    if IP in pacote and pacote.haslayer('UDP') and pacote.dport == 5005:
        ip_origem = pacote[IP].src
        
        try:
            # 2. Extraímos a mensagem (o texto do CSV que o Kali enviou)
            payload = pacote['Raw'].load.decode('utf-8')
            
            # 3. Convertemos a string "0.1, 2.5, 0.0..." numa lista de números reais
            features_reais = [float(x) for x in payload.split(',')]
            
            # 4. Verificação de Segurança: O modelo precisa de exatamente 39 colunas
            if len(features_reais) == len(modelo.feature_name_):
                processar_pacote_em_tempo_real(features_reais, ip_origem)
            else:
                print(f"⚠️ Erro de Formato: Recebidos {len(features_reais)} valores, "
                      f"mas o modelo precisa de {len(modelo.feature_name_)}.")
                      
        except Exception as e:
            # Se o pacote não for o que esperamos, ignoramos para não crashar o script
            pass

print("\nATIVADO: A ouvir a rede eth0...")
try:
    # Este comando fica a ouvir a rede e chama a função 'capturar_pacote' para cada IP que vir
    sniff(iface="eth0", prn=capturar_pacote, store=0)
except KeyboardInterrupt:
    print("\n🛑 Monitorização parada.")
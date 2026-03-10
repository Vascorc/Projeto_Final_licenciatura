import pandas as pd
import numpy as np
import joblib
import os
import warnings
from scapy.all import sniff, IP, TCP, UDP, ICMP

# Ocultar avisos do Scikit-Learn/Pandas para manter o terminal limpo
warnings.filterwarnings("ignore")

# --- 1. CARREGAR OS CÉREBROS DA IA ---
print("A iniciar a analise de rede")
print("A carregar modelo LightGBM e Label Encoder...")

try:
    # Ajusta os caminhos para onde tens os teus ficheiros .pkl
    modelo = joblib.load('./analise_network/modelos/LightGBM/modelo_ciberseguranca_LGBM.pkl')
    le = joblib.load('./analise_network/modelos/LightGBM/label_encoder_categorias.pkl')
    # O modelo precisa de saber exatamente os nomes das colunas que usou no treino
    colunas_treino = modelo.feature_names_in_ 
    print("✅ IA Operacional! À escuta de ameaças...")
except Exception as e:
    print(f"❌ ERRO ao carregar IA: {e}")
    exit()

# Lista para não bloquearmos o mesmo IP repetidamente a cada pacote
ips_bloqueados = []

# --- 2. MOTOR DE MITIGAÇÃO (FIREWALL) ---
def aplicar_mitigacao(ip_atacante, categoria_ataque):
    if ip_atacante in ips_bloqueados:
        return # Já está bloqueado, ignorar
    
    print(f"\n🚨 ALERTA CRÍTICO: {categoria_ataque} detetado vindo de {ip_atacante}!")
    
    # Mapeamento Inteligente para o iptables (Firewall do Linux)
    if categoria_ataque == 'DDoS-TCP' or categoria_ataque == 'DoS-TCP':
        print(f"🛡️ Ação: A bloquear todo o tráfego TCP do IP {ip_atacante}...")
        os.system(f"iptables -A INPUT -s {ip_atacante} -p tcp -j DROP")
        
    elif categoria_ataque == 'DDoS-UDP/ICMP' or categoria_ataque == 'DoS-UDP/ICMP':
        print(f"🛡️ Ação: A bloquear UDP/ICMP do IP {ip_atacante}...")
        os.system(f"iptables -A INPUT -s {ip_atacante} -p udp -j DROP")
        os.system(f"iptables -A INPUT -s {ip_atacante} -p icmp -j DROP")
        
    elif categoria_ataque in ['Mirai-Botnet', 'BruteForce', 'Spoofing', 'Recon', 'Web-Attack']:
        print(f"🛡️ Ação: Isolamento total (Quarentena) do IP {ip_atacante}...")
        os.system(f"iptables -A INPUT -s {ip_atacante} -j DROP")
        
    ips_bloqueados.append(ip_atacante)
    print("✅ Ameaça neutralizada. O Router continua a operar.")

# --- 3. EXTRATOR DE FEATURES (O "OLHEIRO") ---
def processar_pacote(pacote):
    # Só analisamos pacotes IP
    if not pacote.haslayer(IP):
        return

    ip_src = pacote[IP].src
    
    # 3.1. Extrair os dados brutos do pacote (Aproximação para o PoC)
    # Nota de Tese: Num ambiente real, usaríamos um extrator de fluxos (como Zeek) 
    # para calcular a 'Rate', 'Variance', 'AVG' reais. Aqui fazemos uma extração rápida.
    
    dados_pacote = {}
    for col in colunas_treino:
        dados_pacote[col] = 0.0 # Preencher com 0 por defeito
        
    # Preencher as features que conseguimos ler instantaneamente do Scapy
    dados_pacote['Header_Length'] = float(pacote[IP].ihl * 4)
    dados_pacote['Protocol Type'] = float(pacote[IP].proto)
    dados_pacote['Time_To_Live'] = float(pacote[IP].ttl)
    dados_pacote['Tot size'] = float(len(pacote))
    dados_pacote['IPv'] = 1.0 # É IPv4
    
    if pacote.haslayer(TCP):
        dados_pacote['TCP'] = 1.0
        flags = pacote[TCP].flags
        if 'S' in flags: dados_pacote['syn_flag_number'] = 1.0
        if 'A' in flags: dados_pacote['ack_flag_number'] = 1.0
        if 'F' in flags: dados_pacote['fin_flag_number'] = 1.0
        if 'R' in flags: dados_pacote['rst_flag_number'] = 1.0
        if 'P' in flags: dados_pacote['psh_flag_number'] = 1.0
    elif pacote.haslayer(UDP):
        dados_pacote['UDP'] = 1.0
    elif pacote.haslayer(ICMP):
        dados_pacote['ICMP'] = 1.0

    # 3.2. Converter para o formato que a IA entende
    df_pacote = pd.DataFrame([dados_pacote])
    
    # --- FILTRO DE PUREZA UNIVERSAL ---
    df_pacote.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_pacote.fillna(0, inplace=True)
    
    # 3.3. O Cérebro decide
    previsao_numerica = modelo.predict(df_pacote)[0]
    
    # 3.4. Traduzir o número para o nome do ataque usando o Label Encoder
    categoria = le.inverse_transform([previsao_numerica])[0]
    
    # 3.5. Agir!
    if categoria != 'Normal':
        aplicar_mitigacao(ip_src, categoria)

# --- 4. INICIAR A CAPTURA EM TEMPO REAL ---
# IMPORTANTE: Muda o 'iface' para o nome da tua placa de rede no GNS3 (ex: eth0, ens33)
placa_rede = "eth0" # <--- ATENÇÃO AQUI

print(f"🎧 A escutar na interface {placa_rede}...")
# snifamos o tráfego, chamando a função processar_pacote a cada pacote recebido
sniff(iface=placa_rede, prn=processar_pacote, store=False)
import joblib
import os
import time
import pandas as pd
import numpy as np
from scapy.all import sniff, IP

print("-----------A iniciar Sistema de Mitigação no Edge (MODO APRESENTAÇÃO)------------")

# Caminhos 
CAMINHO_MODELO = '../analise_network/modelos/XGBoost/modelo_ciberseguranca_xgb.pkl'
CAMINHO_ENCODER = '../analise_network/modelos/XGBoost/label_encoder_categorias_xgb.pkl'

# SISTEMA DE BLACKLIST 
FICHEIRO_BLACKLIST = "blacklist_ips.txt"
ips_bloqueados = set()

# Carregar IPs que já estavam bloqueados em simulações anteriores
if os.path.exists(FICHEIRO_BLACKLIST):
    with open(FICHEIRO_BLACKLIST, 'r') as f:
        for linha in f:
            ips_bloqueados.add(linha.strip())
print(f"🛡️ Blacklist carregada: {len(ips_bloqueados)} IPs já banidos.\n")

try:
    modelo = joblib.load(CAMINHO_MODELO)
    le = joblib.load(CAMINHO_ENCODER)
    
    pasta_modelo = os.path.dirname(CAMINHO_MODELO)
    ficheiro_scaler = next((f for f in os.listdir(pasta_modelo) if 'scaler' in f.lower() and f.endswith('.pkl')), None)
    
    if ficheiro_scaler:
        scaler = joblib.load(os.path.join(pasta_modelo, ficheiro_scaler))
        print(f"Normalizador (Scaler) carregado: {ficheiro_scaler}")
    else:
        scaler = None

    if hasattr(modelo, 'feature_name_'):
        nomes_features = modelo.feature_name_
    elif hasattr(modelo, 'feature_names_in_'):
        nomes_features = modelo.feature_names_in_
    elif scaler is not None and hasattr(scaler, 'feature_names_in_'):
        nomes_features = scaler.feature_names_in_ 
    else:
        nomes_features = [str(i) for i in range(39)]
        
    n_features = len(nomes_features)

    print("Inteligência Artificial carregada com sucesso!")
    print(f"O modelo está à espera de {n_features} características.")
except Exception as e:
    print(f"Erro ao carregar modelos: {e}")
    exit()


FICHEIRO_LOG_RECON = "alertas_recon.log"

def registar_alerta(mensagem):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {mensagem}"
    print(f"⚠️  {linha}")
    with open(FICHEIRO_LOG_RECON, 'a') as f:
        f.write(linha + "\n")
        
# FUNÇÃO DE EXECUÇÃO DE FIREWALL
def executar_comando(comando):
    os.system(comando)

def aplicar_mitigacao(classe, ip_atacante, tempo_ms):
    if classe in ['DDoS-TCP', 'DoS-TCP']:
        executar_comando(f"iptables -A INPUT -p tcp -s {ip_atacante} -j DROP")
    elif classe in ['DDoS-UDP/ICMP', 'DoS-UDP/ICMP']:
        executar_comando(f"iptables -A INPUT -p udp -s {ip_atacante} -j DROP")
        executar_comando(f"iptables -A INPUT -p icmp -s {ip_atacante} -j DROP")
    elif classe == 'Mirai-Botnet' or classe == 'Spoofing':
        executar_comando(f"iptables -A INPUT -s {ip_atacante} -j DROP")
    elif classe == 'BruteForce':
        executar_comando(f"iptables -A INPUT -p tcp --dport 22 -s {ip_atacante} -j REJECT")
    elif classe == 'Recon':
        registar_alerta(f"[AVISO] Possível reconhecimento detetado - IP: {ip_atacante}")
    
    print(f"--> Mitigação aplicada para: {classe} (IP: {ip_atacante}) - Tempo de IA: {tempo_ms:.2f} ms")


# PROCESSAMENTO EM TEMPO REAL 
def processar_pacote_em_tempo_real(dados_lista, ip_origem):
    df_pacote = pd.DataFrame([dados_lista], columns=nomes_features)
    
    inicio = time.perf_counter()
    
    if scaler is not None:
        X_teste = scaler.transform(df_pacote)
    else:
        X_teste = df_pacote
        
    previsao_num = modelo.predict(X_teste)[0]
    classe_detetada = le.inverse_transform([previsao_num])[0]
    
    fim = time.perf_counter()
    tempo_ms = (fim - inicio) * 1000 
    
    variancia = dados_lista[-1]

    if classe_detetada != 'Normal':
        print(f"ALERTA: {classe_detetada} detetado do IP {ip_origem}! (Variância: {variancia:.2f})")
    
        # Recon não é bloqueado automaticamente — apenas registado
        if classe_detetada == 'Recon':
            aplicar_mitigacao(classe_detetada, ip_origem, tempo_ms)
        else:
            if ip_origem not in ips_bloqueados:
                ips_bloqueados.add(ip_origem)
                with open(FICHEIRO_BLACKLIST, 'a') as f:
                    f.write(ip_origem + "\n")
            aplicar_mitigacao(classe_detetada, ip_origem, tempo_ms)
    else:
        print(f"Tráfego Normal de {ip_origem}. (Variância: {variancia:.2f})")

# MODO ESCUTA
def capturar_pacote(pacote):
    if IP in pacote and pacote.haslayer('UDP') and pacote.dport == 5005:
        ip_origem = pacote[IP].src
        
        # --- VERIFICAÇÃO DE BLACKLIST IMEDIATA ---
        if ip_origem in ips_bloqueados:
            print(f"⛔ DESCARTADO: O IP {ip_origem} está na Blacklist (Ataque Travado sem IA!)")
            return # Aborta o processamento aqui, poupando CPU máximo
        
        try:
            payload = pacote['Raw'].load.decode('utf-8')
            features_reais = [float(x) for x in payload.split(',')]
            
            if len(features_reais) == n_features:
                processar_pacote_em_tempo_real(features_reais, ip_origem)
            else:
                print(f"Erro de Formato: Recebidos {len(features_reais)} valores, mas o modelo precisa de {n_features}.")
                      
        except Exception as e:
            pass # Ignoramos erros de descodificação para manter o ecrã limpo na apresentação

print("\nATIVADO: A ouvir a rede...")
try:
    sniff(iface="h2-eth0", prn=capturar_pacote, store=0)
except KeyboardInterrupt:
    print("\nMonitorização parada pelo utilizador.")
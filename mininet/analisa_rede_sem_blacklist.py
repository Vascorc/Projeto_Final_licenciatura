import joblib
import os
import time
import csv
from datetime import datetime
import pandas as pd
import numpy as np
from scapy.all import sniff, IP

print("-----------A iniciar Sistema de Mitigação no Edge------------")

# Caminhos 
CAMINHO_MODELO = '../analise_network/modelos/XGBoost/modelo_ciberseguranca_xgb.pkl'
CAMINHO_ENCODER = '../analise_network/modelos/XGBoost/label_encoder_categorias_xgb.pkl'

# --- NOVO: BUFFER EM MEMÓRIA RAM PARA EVITAR LENTIDÃO DE DISCO ---
buffer_logs = []
# -----------------------------------------------------------------

try:
    modelo = joblib.load(CAMINHO_MODELO)
    le = joblib.load(CAMINHO_ENCODER)
    
    # Carregar o Scaler caso exista na mesma pasta. 
    pasta_modelo = os.path.dirname(CAMINHO_MODELO)
    ficheiro_scaler = next((f for f in os.listdir(pasta_modelo) if 'scaler' in f.lower() and f.endswith('.pkl')), None)
    
    if ficheiro_scaler:
        scaler = joblib.load(os.path.join(pasta_modelo, ficheiro_scaler))
        print(f"Normalizador (Scaler) carregado: {ficheiro_scaler}")
    else:
        scaler = None

    # Obter nomes das colunas de forma segura
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

def executar_comando(comando):
    os.system(comando)

# ALTERADO: Agora apenas adiciona à lista na RAM (Super Rápido!)
def registar_log_memoria(ip_origem, classe, acao, tempo_ms):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    nome_modelo = CAMINHO_MODELO.split('/')[-2]
    
    # Guarda temporariamente na RAM
    buffer_logs.append([agora, nome_modelo, ip_origem, classe, acao, round(tempo_ms, 4)])

# NOVA FUNÇÃO: Escreve tudo no disco quando fechas o programa
def descarregar_buffer_para_csv():
    if not buffer_logs:
        print("\nNenhum dado capturado para guardar.")
        return
        
    ficheiro = "./dados_apos_ataque/historico_testes_modelos.csv"
    os.makedirs(os.path.dirname(ficheiro), exist_ok=True)
    existe = os.path.isfile(ficheiro)
    
    print(f"\n💾 A gravar {len(buffer_logs)} registos no disco... Por favor aguarda!")
    with open(ficheiro, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["DataHora", "Modelo_IA", "IP_Origem", "Classe_Detetada", "Acao_Tomada", "Tempo_Resposta_ms"])
        writer.writerows(buffer_logs) # Escreve as milhares de linhas de uma só vez!
    print("✅ Todos os dados foram guardados com sucesso no CSV!")

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
    
    print(f"-->Mitigação aplicada para: {classe} (IP: {ip_atacante}) - Tempo de IA: {tempo_ms:.2f} ms")

#  PROCESSAMENTO EM TEMPO REAL 
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
        aplicar_mitigacao(classe_detetada, ip_origem, tempo_ms)
        acao = "Bloqueado"
    else:
        print(f"Tráfego Normal de {ip_origem}. (Variância: {variancia:.2f})")
        acao = "Permitido"
        
    # Guardar na RAM em vez do arquivo físico
    registar_log_memoria(ip_origem, classe_detetada, acao, tempo_ms)
 
# MODO ESCUTA
def capturar_pacote(pacote):
    if IP in pacote and pacote.haslayer('UDP') and pacote.dport == 5005:
        ip_origem = pacote[IP].src
        
        try:
            payload = pacote['Raw'].load.decode('utf-8')
            features_reais = [float(x) for x in payload.split(',')]
            
            if len(features_reais) == n_features:
                processar_pacote_em_tempo_real(features_reais, ip_origem)
            else:
                print(f"Erro de Formato: Recebidos {len(features_reais)} valores, "
                      f"mas o modelo precisa de {n_features}.")
                      
        except Exception as e:
            print(f"Erro interno ao processar pacote: {e}")

print("\nATIVADO: A ouvir a rede...")
try:
    sniff(iface="h2-eth0", prn=capturar_pacote, store=0)
except KeyboardInterrupt:
    print("\n Monitorização parada pelo utilizador.")
finally:
    # IMPORTANTE: Garante que descarrega os dados se o utilizador fechar ou carregar Ctrl+C
    descarregar_buffer_para_csv()
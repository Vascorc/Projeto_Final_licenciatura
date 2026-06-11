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
    
    # Carregar o Scaler caso exista na mesma pasta. 
    #O Scaler serve para colocar todos os valores de entrada na mesma escala (ex: 0 a 1)
    # para que modelos como as Redes Neuronais (MLP) não fiquem enviesados por valores altos.
    # Modelos de árvore (LightGBM, Random Forest) não precisam, por isso ele só carrega se existir.
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



# FUNÇÃO DE EXECUÇÃO DE FIREWALL E LOGS 
def executar_comando(comando):
    os.system(comando)
    # pass # comentado apenas para simulação, em caso real a execucao do comando é realizada

def registar_log_csv(ip_origem, classe, acao, tempo_ms):
    ficheiro = "./dados_apos_ataque/historico_testes_modelos.csv"
    # Criar a diretoria se não existir para não dar erro
    os.makedirs(os.path.dirname(ficheiro), exist_ok=True)
    
    existe = os.path.isfile(ficheiro)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # extrair o nome do modelo a partir do caminho que estás a usar
    nome_modelo = CAMINHO_MODELO.split('/')[-2]
    
    with open(ficheiro, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["DataHora", "Modelo_IA", "IP_Origem", "Classe_Detetada", "Acao_Tomada", "Tempo_Resposta_ms"])
        writer.writerow([agora, nome_modelo, ip_origem, classe, acao, round(tempo_ms, 4)])

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
    # Convertemos a lista para DataFrame
    df_pacote = pd.DataFrame([dados_lista], columns=nomes_features)
    
    # Iniciar temporizador
    inicio = time.perf_counter()
    
    # IMPORTANTE: Se tivermos um Scaler (MLP), temos de normalizar os dados antes de prever!
    if scaler is not None:
        X_teste = scaler.transform(df_pacote)
    else:
        X_teste = df_pacote
        
    # Previsão
    previsao_num = modelo.predict(X_teste)[0]
    classe_detetada = le.inverse_transform([previsao_num])[0]
    
    # Parar temporizador
    fim = time.perf_counter()
    tempo_ms = (fim - inicio) * 1000 # Converter de segundos para milissegundos
    
    # A variância é a última feature na lista (índice -1)
    variancia = dados_lista[-1]

    if classe_detetada != 'Normal':
        print(f"ALERTA: {classe_detetada} detetado do IP {ip_origem}! (Variância: {variancia:.2f})")
        
        # --- NOVO: ADICIONAR À BLACKLIST ---
        if ip_origem not in ips_bloqueados:
            ips_bloqueados.add(ip_origem)
            with open(FICHEIRO_BLACKLIST, 'a') as f:
                f.write(ip_origem + "\n")
        # -----------------------------------
        
        aplicar_mitigacao(classe_detetada, ip_origem, tempo_ms)
        acao = "Bloqueado"
    else:
        print(f"Tráfego Normal de {ip_origem}. (Variância: {variancia:.2f})")
        acao = "Permitido"
        
    # Guardar os dados no Excel/CSV para a tua tese
    registar_log_csv(ip_origem, classe_detetada, acao, tempo_ms)
 
# MODO ESCUTA
def capturar_pacote(pacote):
    # Verificamos se é um pacote IP e se traz dados UDP na porta 5005
    if IP in pacote and pacote.haslayer('UDP') and pacote.dport == 5005:
        ip_origem = pacote[IP].src
        
        # --- NOVO: VERIFICAÇÃO DE BLACKLIST ANTES DE PROCESSAR ---
        if ip_origem in ips_bloqueados:
            print(f"⛔ DESCARTADO: O IP {ip_origem} está na Blacklist (Ataque Travado sem IA!)")
            return # Aborta o processamento aqui, poupando CPU
        # ---------------------------------------------------------
        
        try:
            # Extraímos a mensagem (o texto do CSV que é enviado)
            payload = pacote['Raw'].load.decode('utf-8')
            
            # Convertemos a string "0.1, 2.5, 0.0..." numa lista de números reais
            features_reais = [float(x) for x in payload.split(',')]
            
            # Verificação de Segurança
            if len(features_reais) == n_features:
                processar_pacote_em_tempo_real(features_reais, ip_origem)
            else:
                print(f"Erro de Formato: Recebidos {len(features_reais)} valores, "
                      f"mas o modelo precisa de {n_features}.")
                      
        except Exception as e:
            # Mostramos o erro caso rebente, em vez de o silenciar com 'pass'
            print(f"Erro interno ao processar pacote: {e}")

print("\nATIVADO: A ouvir a rede...")
try:
    # Este comando fica a ouvir todas as interfaces e chama a função 'capturar_pacote' para cada IP que vir
    # MUDANÇA PARA TOPOLOGIA NOVA: Se usares o ServidorIA, a interface é "any". 
    # Se testares sem ele, podes meter "Defensor-eth0" novamente.
    sniff(iface="any", prn=capturar_pacote, store=0)
except KeyboardInterrupt:
    print("\n Monitorização parada.")
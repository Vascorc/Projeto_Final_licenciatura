import joblib
import os
import time
import csv
from datetime import datetime
import pandas as pd
import numpy as np
from scapy.all import sniff, IP

print("-----------A iniciar Sistema de Mitigação no Edge (MODO RECOLHA COM ID)------------")

CAMINHO_MODELO = '../../analise_network/modelos/XGBoost/modelo_ciberseguranca_xgb.pkl'
CAMINHO_ENCODER = '../../analise_network/modelos/XGBoost/label_encoder_categorias_xgb.pkl'

buffer_logs = []

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
except Exception as e:
    print(f"Erro ao carregar modelos: {e}")
    exit()

def executar_comando(comando):
    pass # Desativado para garantir velocidade máxima sem travar o CPU

def registar_log_memoria(packet_id, ip_origem, classe, acao, tempo_ms):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    nome_modelo = CAMINHO_MODELO.split('/')[-2]
    # Guardamos o packet_id original na primeira posição!
    buffer_logs.append([packet_id, agora, nome_modelo, ip_origem, classe, acao, round(tempo_ms, 4)])

def descarregar_buffer_para_csv():
    if not buffer_logs:
        print("\nNenhum dado capturado para guardar.")
        return
        
    # Podes usar só o nome do ficheiro, já que estás a correr dentro da pasta certa
    ficheiro = "historico_testes_modelos.csv" 
    
    # CORREÇÃO: Só tenta criar a pasta se realmente existir um caminho definido
    diretorio = os.path.dirname(ficheiro)
    if diretorio: 
        os.makedirs(diretorio, exist_ok=True)
        
    existe = os.path.isfile(ficheiro)
    
    print(f"\n💾 A gravar {len(buffer_logs)} registos no disco... Por favor aguarda!")
    try:
        with open(ficheiro, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not existe:
                # Cabeçalho com o Packet_ID incluído
                writer.writerow(["Packet_ID", "DataHora", "Modelo_IA", "IP_Origem", "Classe_Detetada", "Acao_Tomada", "Tempo_Resposta_ms"])
            writer.writerows(buffer_logs)
        print("✅ Todos os dados foram guardados com sucesso no CSV!")
    except Exception as e:
        print(f"❌ Erro fatal ao gravar no ficheiro: {e}")

def processar_pacote_em_tempo_real(packet_id, dados_lista, ip_origem):
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
        print(f"ALERTA: {classe_detetada} detetado! (ID Original: {packet_id})")
    else:
        print(f"Tráfego Normal. (ID Original: {packet_id})")
        
    registar_log_memoria(packet_id, ip_origem, classe_detetada, "Permitido", tempo_ms)
 
def capturar_pacote(pacote):
    if IP in pacote and pacote.haslayer('UDP') and pacote.dport == 5005:
        ip_origem = pacote[IP].src
        try:
            payload = pacote['Raw'].load.decode('utf-8')
            valores = payload.split(',')
            
            # O primeiro valor é o nosso Packet_ID (número inteiro)
            packet_id = int(valores[0])
            
            # O resto dos valores (índices 1 em diante) são as características para a IA
            features_reais = [float(x) for x in valores[1:]]
            
            if len(features_reais) == n_features:
                processar_pacote_em_tempo_real(packet_id, features_reais, ip_origem)
        except Exception as e:
            pass

print("\nATIVADO: A ouvir a rede...")
try:
    sniff(iface="h2-eth0", prn=capturar_pacote, store=0)
except KeyboardInterrupt:
    print("\n Monitorização parada pelo utilizador.")
finally:
    descarregar_buffer_para_csv()
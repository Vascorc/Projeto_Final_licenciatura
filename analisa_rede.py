import joblib
import os
import subprocess
# import paho.mqtt.client as mqtt # Parte de MQTT comentada

# --- 1. CONFIGURAÇÃO E CARREGAMENTO ---
print("🚀 A iniciar Sistema de Mitigação no Edge...")

# Caminhos para os ficheiros que já criaste
CAMINHO_MODELO = './LightGBM/modelo_ciberseguranca_lgbm.pkl'
CAMINHO_ENCODER = './LightGBM/label_encoder_categorias_lgbm.pkl'

try:
    modelo = joblib.load(CAMINHO_MODELO)
    le = joblib.load(CAMINHO_ENCODER)
    print("✅ Inteligência Artificial carregada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar modelos: {e}")
    exit()

# --- 2. FUNÇÃO DE EXECUÇÃO DE FIREWALL (iptables) ---
def executar_comando(comando):
    """Executa o comando no sistema operativo."""
    print(f"🛠️ A executar: {comando}")
    # os.system(comando) # Descomenta para aplicar no router real
    # No laboratório, apenas imprimimos para segurança.

def aplicar_mitigacao(classe, ip_atacante):
    """Aplica a regra de firewall específica baseada na anomalia detetada."""
    
    if classe in ['DDoS-TCP', 'DoS-TCP']:
        # Mitigação: Bloqueio total de pedidos SYN excessivos
        executar_comando(f"iptables -A INPUT -p tcp -s {ip_atacante} -j DROP")
        print(f"🛡️ Mitigação aplicada: Bloqueio de inundação TCP de {ip_atacante}")

    elif classe in ['DDoS-UDP/ICMP', 'DoS-UDP/ICMP']:
        # Mitigação: Rate Limiting ou Drop para inundação sem conexão
        executar_comando(f"iptables -A INPUT -p udp -s {ip_atacante} -j DROP")
        executar_comando(f"iptables -A INPUT -p icmp -s {ip_atacante} -j DROP")
        print(f"🛡️ Mitigação aplicada: Filtro UDP/ICMP para {ip_atacante}")

    elif classe == 'Mirai-Botnet':
        # Mitigação: Quarentena Total (Amputação da rede)
        executar_comando(f"iptables -A INPUT -s {ip_atacante} -j DROP")
        executar_comando(f"iptables -A FORWARD -s {ip_atacante} -j DROP")
        print(f"🛡️ Mitigação aplicada: Quarentena Total para Botnet Mirai em {ip_atacante}")

    elif classe == 'BruteForce':
        # Mitigação: Bloqueio imediato da porta de gestão (ex: SSH porta 22)
        executar_comando(f"iptables -A INPUT -p tcp --dport 22 -s {ip_atacante} -j REJECT")
        print(f"🛡️ Mitigação aplicada: Acesso SSH rejeitado para {ip_atacante}")

    elif classe == 'Recon':
        # Mitigação: Tornar o router invisível ao atacante (Drop silencioso)
        executar_comando(f"iptables -A INPUT -s {ip_atacante} -j DROP")
        print(f"🛡️ Mitigação aplicada: Silenciamento de Scanning de {ip_atacante}")

    elif classe == 'Spoofing':
        # Mitigação: Bloqueio de pacotes com identidade falsificada
        executar_comando(f"iptables -A INPUT -s {ip_atacante} -j DROP")
        print(f"🛡️ Mitigação aplicada: Bloqueio de IP Spoofing de {ip_atacante}")

    # --- ESPAÇO PARA MQTT (COMENTADO) ---
    # msg_alerta = f"Anomalia: {classe} detetada do IP {ip_atacante}"
    # client.publish("cidade/seguranca/alertas", msg_alerta)

# --- 3. SIMULAÇÃO DE FUNCIONAMENTO ---
# Na vida real, estes dados viriam dos pacotes que o router recebe
def processar_pacote_em_tempo_real(dados_pacote, ip_origem):
    # O modelo faz a previsão (recebe um número)
    previsao_num = modelo.predict([dados_pacote])[0]
    
    # O LabelEncoder traduz o número para o nome do ataque
    classe_detetada = le.inverse_transform([previsao_num])[0]
    
    if classe_detetada != 'Normal':
        print(f"⚠️ ALERTA: {classe_detetada} detetado!")
        aplicar_mitigacao(classe_detetada, ip_origem)
    else:
        print("🟢 Tráfego Normal.")

# Exemplo de teste (Simulação)
# Substituir pelos valores de 1 linha de features do teu dataset
exemplo_pacote = [0] * 46 # Simulação de 46 features
processar_pacote_em_tempo_real(exemplo_pacote, "192.168.1.50")
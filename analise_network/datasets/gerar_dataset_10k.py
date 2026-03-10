import pandas as pd
import gc

# --- CONFIGURAÇÃO ---
# Agora vamos ler 4 ficheiros! (Certifica-te que já os descarregaste)
ficheiros = [
    './Merged01.csv',
    './Merged02.csv',
    './Merged03.csv',
    './Merged04.csv'
]
caminho_saida = './dataset_treino_balanceado_10k.csv'
LIMITE_POR_CLASSE = 10000

print("⚙️ A INICIAR O MOTOR DE EXTRACÇÃO MULTI-VOLUME...")

# --- 1. CARREGAMENTO OTIMIZADO DE MEMÓRIA ---
lista_dfs = []
total_pacotes = 0

for ficheiro in ficheiros:
    print(f" -> A carregar {ficheiro}...")
    try:
        df_temp = pd.read_csv(ficheiro, low_memory=False)
        lista_dfs.append(df_temp)
        total_pacotes += len(df_temp)
    except FileNotFoundError:
        print(f"❌ ERRO: Não encontrei o {ficheiro}. Já fizeste o download?")
        exit()

print(" -> A fundir os 4 volumes...")
df = pd.concat(lista_dfs, ignore_index=True)

# Limpar RAM!
del lista_dfs, df_temp
gc.collect()

print(f"✅ Total do 'Oceano' de Dados: {total_pacotes} pacotes.")

# --- 2. APLICAR AS NOSSAS CATEGORIAS ---
print("2. A organizar os pacotes pelas categorias do Edge Router...")
def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    if label == 'BENIGNTRAFFIC': return 'Normal'
    if 'DDOS' in label: return 'DDoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DDoS-UDP/ICMP'
    if 'DOS' in label: return 'DoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DoS-UDP/ICMP'
    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    if 'WEB' in label: return 'Web-Attack'
    return 'Outros'

df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

# --- 3. A MAGIA DO UNDERSAMPLING ---
print(f"3. A pescar as {LIMITE_POR_CLASSE} amostras de cada classe...")

lista_de_amostras = []

for nome_categoria, grupo in df.groupby('categoria'):
    if len(grupo) > LIMITE_POR_CLASSE:
        lista_de_amostras.append(grupo.sample(n=LIMITE_POR_CLASSE, random_state=42))
    else:
        lista_de_amostras.append(grupo)

df_balanceado = pd.concat(lista_de_amostras)
df_balanceado = df_balanceado.sample(frac=1, random_state=42).reset_index(drop=True)

print("\n📊 DISTRIBUIÇÃO DO NOVO SUPER DATASET DE ELITE:")
print(df_balanceado['categoria'].value_counts())

# --- 4. GUARDAR ---
print("\n4. A guardar o ficheiro super leve...")
df_balanceado.to_csv(caminho_saida, index=False)

print(f"🚀 FEITO! Novo dataset guardado em: {caminho_saida}")
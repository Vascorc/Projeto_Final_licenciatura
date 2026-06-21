import pandas as pd
import gc

# --- CONFIGURAÇÃO ---
ficheiros = [
    './Merged06.csv',
    './Merged07.csv',
    './Merged08.csv',
    './Merged09.csv',
    './Merged10.csv',
]

# NOVO NOME PARA NÃO SOBRESCREVER O TEU FICHEIRO DE TESTES
caminho_saida = './dataset_validar_treino.csv'

# O NÚMERO MÁGICO PARA TREINO DE IAs: 10 Mil pacotes por categoria
LIMITE_POR_CLASSE = 10000

print("⚙️ A INICIAR O MOTOR DE EXTRACÇÃO PARA TREINO...")

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

print(" -> A fundir os volumes...")
df = pd.concat(lista_dfs, ignore_index=True)

# Limpar RAM!
del lista_dfs, df_temp
gc.collect()

print(f"✅ Total do 'Oceano' de Dados: {total_pacotes} pacotes.")

# --- 2. APLICAR AS NOSSAS CATEGORIAS ---
print("2. A organizar os pacotes pelas categorias do Edge Router...")
def categorizar_ataque_mitigacao(label):
    label = str(label).strip().upper() 
    
    # CORREÇÃO À PROVA DE BALA: Apanha qualquer variação de tráfego legítimo
    if 'BENIGN' in label or 'NORMAL' in label: return 'Normal'
    
    if 'DDOS' in label: return 'DDoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DDoS-UDP/ICMP'
    if 'DOS' in label: return 'DoS-TCP' if ('TCP' in label or 'SYN' in label or 'HTTP' in label) else 'DoS-UDP/ICMP'
    if 'MIRAI' in label: return 'Mirai-Botnet'
    if 'BRUTE' in label: return 'BruteForce'
    if 'SPOOFING' in label: return 'Spoofing'
    if 'RECON' in label: return 'Recon'
    # if 'WEB' in label: return 'Web-Attack'
    return 'Outros'

# Aplicar a função e remover possíveis linhas vazias (NaN) que existam no Label original
df = df.dropna(subset=['Label'])
df['categoria'] = df['Label'].apply(categorizar_ataque_mitigacao)

# --- 3. A MAGIA DO UNDERSAMPLING ---
print(f"3. A pescar as {LIMITE_POR_CLASSE} amostras de cada classe para o treino...")

lista_de_amostras = []

for nome_categoria, grupo in df.groupby('categoria'):
    if len(grupo) > LIMITE_POR_CLASSE:
        lista_de_amostras.append(grupo.sample(n=LIMITE_POR_CLASSE, random_state=42))
    else:
        # Se alguma classe tiver menos de 10k, apanha todas as que tiver
        lista_de_amostras.append(grupo)

df_balanceado = pd.concat(lista_de_amostras)
# Baralhar os dados (frac=1) para a IA não viciar a aprendizagem
df_balanceado = df_balanceado.sample(frac=1, random_state=42).reset_index(drop=True)

print("\n📊 DISTRIBUIÇÃO DO NOVO DATASET DE TREINO CORRIGIDO:")
print(df_balanceado['categoria'].value_counts())

# --- 4. GUARDAR ---
print("\n4. A guardar o ficheiro...")
df_balanceado.to_csv(caminho_saida, index=False)

print(f"🚀 FEITO! Novo dataset de treino pronto em: {caminho_saida}")
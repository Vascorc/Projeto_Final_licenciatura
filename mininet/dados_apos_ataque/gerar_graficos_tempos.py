import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import confusion_matrix

CAMINHO_RESULTADOS = 'historico_testes_modelos.csv'
CAMINHO_ORIGINAL = '../../analise_network/datasets/dataset_validar_treino.csv'

print("🚀 A iniciar o motor de análise gráfica da IA...\n")

if not os.path.exists(CAMINHO_RESULTADOS):
    print(f"❌ ERRO: O ficheiro de resultados {CAMINHO_RESULTADOS} não foi encontrado.")
    exit()
if not os.path.exists(CAMINHO_ORIGINAL):
    print(f"❌ ERRO: O dataset original {CAMINHO_ORIGINAL} não foi encontrado.")
    exit()

print("🔍 A carregar os datasets e a realizar o cruzamento por Packet_ID...")
df_resultados = pd.read_csv(CAMINHO_RESULTADOS)
df_original = pd.read_csv(CAMINHO_ORIGINAL)

# CORREÇÃO: Capturar o nome da coluna alvo ANTES de adicionar o Packet_ID ao final!
coluna_alvo_real = df_original.columns[-1]

df_original['Packet_ID'] = df_original.index 

df = pd.merge(df_resultados, df_original, on='Packet_ID', how='inner')

if df.empty:
    print("❌ ERRO: O cruzamento falhou. Certifica-te que os Packet_IDs batem certo.")
    exit()

print(f"✅ Cruzamento perfeito! {len(df)} pacotes validados matematicamente.\n")

df['Acerto'] = df['Classe_Detetada'] == df[coluna_alvo_real]

sns.set_theme(style="whitegrid")

# GRÁFICO 1: TEMPO MÉDIO
print("📊 A desenhar: Tempo Médio de Inferência por Modelo...")
plt.figure(figsize=(10, 6))
tempos_medios = df.groupby('Modelo_IA')['Tempo_Resposta_ms'].mean().reset_index()
tempos_medios = tempos_medios.sort_values(by='Tempo_Resposta_ms')
# CORREÇÃO SEABORN: Adicionado hue e legend=False
ax = sns.barplot(x='Modelo_IA', y='Tempo_Resposta_ms', hue='Modelo_IA', data=tempos_medios, palette='viridis', edgecolor='black', legend=False)
plt.title('Tempo Médio de Inferência por Modelo de IA', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Modelo de Inteligência Artificial', fontsize=12, fontweight='bold')
for i, v in enumerate(tempos_medios['Tempo_Resposta_ms']):
    ax.text(i, v + (v * 0.02), f"{v:.4f} ms", ha='center', fontweight='bold', fontsize=11)
plt.tight_layout()
plt.savefig('grafico_tempo_medio_modelos.png', dpi=300)

# GRÁFICO 2: BOXPLOT
print("📊 A desenhar: Boxplot de Estabilidade da Latência...")
plt.figure(figsize=(12, 7))
sns.boxplot(x='Modelo_IA', y='Tempo_Resposta_ms', hue='Modelo_IA', data=df, palette='Set2', legend=False)
plt.title('Variação e Estabilidade da Latência (Boxplot)', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Modelo de Inteligência Artificial', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('grafico_boxplot_modelos.png', dpi=300)

# GRÁFICO 3: TEMPO POR CLASSE
print("📊 A desenhar: Tempo Médio por Classe Detetada...")
plt.figure(figsize=(14, 7))
sns.barplot(x='Classe_Detetada', y='Tempo_Resposta_ms', hue='Modelo_IA', data=df, palette='muted', edgecolor='black', errorbar=None)
plt.title('Tempo Médio de Resposta por Classe de Tráfego', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Tipo de Tráfego Detetado', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontweight='bold')
plt.legend(title='Modelo Usado', fontsize=11)
plt.tight_layout()
plt.savefig('grafico_tempo_por_classe.png', dpi=300)

# GRÁFICO 4: ACCURACY
print("📊 A desenhar: Taxa de Acertos Global...")
plt.figure(figsize=(10, 6))
precisao = df.groupby('Modelo_IA')['Acerto'].mean() * 100
precisao = precisao.reset_index()
sns.barplot(x='Modelo_IA', y='Acerto', hue='Modelo_IA', data=precisao, palette='coolwarm', edgecolor='black', legend=False)
plt.title('Precisão Global de Deteção (Accuracy %)', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Taxa de Acerto (%)', fontsize=12, fontweight='bold')
plt.xlabel('Modelo de Inteligência Artificial', fontsize=12, fontweight='bold')
plt.ylim(0, 105)
for i, v in enumerate(precisao['Acerto']):
    plt.text(i, v + 1.5, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_precisao_modelos.png', dpi=300)

# GRÁFICO 5: MATRIZ DE CONFUSÃO (Uma para cada modelo)
print("📊 A desenhar: Matrizes de Confusão (Obrigatório em teses de IA)...")

modelos_unicos = df['Modelo_IA'].unique()

for modelo in modelos_unicos:
    df_modelo = df[df['Modelo_IA'] == modelo]

    # Transforma tudo para string garantindo que não há mistura de tipos de dados
    classes_reais = df_modelo[coluna_alvo_real].astype(str)
    classes_previstas = df_modelo['Classe_Detetada'].astype(str)

    classes_unicas = sorted(list(set(classes_reais.unique()) | set(classes_previstas.unique())))

    matriz = confusion_matrix(classes_reais, classes_previstas, labels=classes_unicas)
    df_cm = pd.DataFrame(matriz, index=classes_unicas, columns=classes_unicas)

    plt.figure(figsize=(12, 9))
    sns.heatmap(df_cm, annot=True, fmt='d', cmap='Blues', linewidths=1, linecolor='black')
    plt.title(f'Matriz de Confusão - {modelo}', fontsize=16, fontweight='bold', pad=15)
    plt.ylabel('Classe Real (Dataset)', fontsize=12, fontweight='bold')
    plt.xlabel('Classe Detetada (IA)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Limpa espaços no nome do ficheiro para evitar erros no Linux
    nome_ficheiro = f'grafico_matriz_confusao_{modelo.replace(" ", "_")}.png'
    plt.savefig(nome_ficheiro, dpi=300)
    plt.close() # Liberta a memória gráfica do PC após cada desenho

print("\n🏁 SUCESSO! Gráficos académicos gerados e prontos para o teu relatório:")
print("  👉 grafico_tempo_medio_modelos.png")
print("  👉 grafico_boxplot_modelos.png")
print("  👉 grafico_tempo_por_classe.png")
print("  👉 grafico_precisao_modelos.png")
print("  👉 E 4 Matrizes de Confusão (uma por modelo)!")
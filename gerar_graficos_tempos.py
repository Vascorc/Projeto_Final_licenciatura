import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

CAMINHO_CSV = 'historico_testes_modelos.csv'
CAMINHO_REAL = './analise_network/datasets/dataset_ataque_pequeno.csv'

print("🚀 A iniciar o gerador de gráficos da tese...\n")

# Verificar se os ficheiros existem
if not os.path.exists(CAMINHO_CSV) or not os.path.exists(CAMINHO_REAL):
    print(f"❌ ERRO: Faltam ficheiros (preciso do {CAMINHO_CSV} e do {CAMINHO_REAL}).")
    exit()

# Carregar os dados
df = pd.read_csv(CAMINHO_CSV)
df_real = pd.read_csv(CAMINHO_REAL)

if df.empty:
    print("❌ ERRO: O ficheiro CSV está vazio.")
    exit()

print(f"✅ Dados carregados. A processar {len(df)} pacotes...\n")

# --- NOVO: CÁLCULO DE PRECISÃO GLOBAL ---
# Alinhamos as etiquetas reais do dataset com os resultados dos testes
n_modelos = len(df['Modelo_IA'].unique())
categorias_reais = np.tile(df_real['categoria'].values, n_modelos)
df['Classe_Real'] = categorias_reais
df['Acertou'] = df['Classe_Real'] == df['Classe_Detetada']

# Configurar estilo visual
plt.style.use('seaborn-v0_8-whitegrid')

# GRÁFICO 1: TEMPO MÉDIO DE RESPOSTA GERAL
print("📊 A desenhar: Tempo Médio de Inferência...")
plt.figure(figsize=(10, 6))
tempos_medios = df.groupby('Modelo_IA')['Tempo_Resposta_ms'].mean().reset_index().sort_values(by='Tempo_Resposta_ms')
ax1 = sns.barplot(x='Modelo_IA', y='Tempo_Resposta_ms', data=tempos_medios, palette='viridis', edgecolor='black')
plt.title('Tempo Médio de Inferência por Modelo de IA', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
for i, v in enumerate(tempos_medios['Tempo_Resposta_ms']):
    ax1.text(i, v + (v * 0.02), f"{v:.4f} ms", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('grafico_tempo_medio_modelos.png', dpi=300)

# GRÁFICO 2: BOXPLOT DA ESTABILIDADE
print("📊 A desenhar: Estabilidade (Boxplot)...")
plt.figure(figsize=(12, 7))
sns.boxplot(x='Modelo_IA', y='Tempo_Resposta_ms', data=df, palette='Set2')
plt.title('Variação e Estabilidade da Latência (Boxplot)', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('grafico_boxplot_modelos.png', dpi=300)

# GRÁFICO 3: PRECISÃO GLOBAL (ACCURACY) - O NOVO GRÁFICO!
print("📊 A desenhar: Comparação de Precisão Global (Accuracy)...")
plt.figure(figsize=(10, 6))
# Calcular a média de acertos (Accuracy) por modelo
precisao_df = df.groupby('Modelo_IA')['Acertou'].mean().reset_index()
precisao_df['Accuracy'] = precisao_df['Acertou'] * 100
precisao_df = precisao_df.sort_values(by='Accuracy', ascending=False)

ax3 = sns.barplot(x='Modelo_IA', y='Accuracy', data=precisao_df, palette='magma', edgecolor='black')
plt.title('Taxa de Sucesso (Accuracy) Global por Modelo', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Precisão (%)', fontsize=12, fontweight='bold')
plt.ylim(0, 110) # Espaço para o texto no topo

for i, v in enumerate(precisao_df['Accuracy']):
    ax3.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('grafico_comparacao_precisao.png', dpi=300)

# GRÁFICO 4: TEMPO POR TIPO DE ANOMALIA
print("📊 A desenhar: Tempo Médio por Classe...")
plt.figure(figsize=(14, 7))
sns.barplot(x='Classe_Detetada', y='Tempo_Resposta_ms', hue='Modelo_IA', data=df, palette='muted', edgecolor='black', errorbar=None)
plt.title('Tempo Médio de Resposta por Classe de Tráfego', fontsize=16, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('grafico_tempo_por_classe.png', dpi=300)

# GRÁFICO 5: CONTAGEM DE DETEÇÕES
print("📊 A desenhar: Contagem de Deteções...")
plt.figure(figsize=(14, 7))
ax5 = sns.countplot(x='Classe_Detetada', hue='Modelo_IA', data=df, palette='Set1', edgecolor='black')
plt.axhline(y=10, color='red', linestyle='--', linewidth=2, label='Esperado (10 pacotes)')
plt.title('Contagem de Deteções por Classe de Tráfego', fontsize=16, fontweight='bold', pad=15)
plt.legend(title='Modelo Usado')
for container in ax5.containers:
    ax5.bar_label(container, padding=3, fontweight='bold')
plt.tight_layout()
plt.savefig('grafico_contagem_precisao.png', dpi=300)

print("\n🏁 SUCESSO! Cinco gráficos criados com sucesso.")
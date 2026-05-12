import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CAMINHO_CSV = 'historico_testes_modelos.csv'

print("🚀 A iniciar o gerador de gráficos de latência da IA...\n")

# Verificar se o ficheiro existe
if not os.path.exists(CAMINHO_CSV):
    print(f"❌ ERRO: O ficheiro {CAMINHO_CSV} ainda não existe.")
    print("Corre primeiro o teu 'analisa_rede.py' com alguns ataques para gerar dados!")
    exit()

# Carregar os dados
df = pd.read_csv(CAMINHO_CSV)

if df.empty:
    print("❌ ERRO: O ficheiro CSV está vazio. Não há dados para desenhar.")
    exit()

print(f"✅ Ficheiro CSV carregado com sucesso. {len(df)} pacotes analisados.\n")

# Configurar estilo visual (moderno e limpo)
plt.style.use('seaborn-v0_8-whitegrid')

# GRÁFICO 1: TEMPO MÉDIO DE RESPOSTA GERAL
print("📊 A desenhar: Tempo Médio de Inferência por Modelo...")
plt.figure(figsize=(10, 6))

# Calcular as médias
tempos_medios = df.groupby('Modelo_IA')['Tempo_Resposta_ms'].mean().reset_index()
tempos_medios = tempos_medios.sort_values(by='Tempo_Resposta_ms')

ax = sns.barplot(x='Modelo_IA', y='Tempo_Resposta_ms', data=tempos_medios, palette='viridis', edgecolor='black')
plt.title('Tempo Médio de Inferência por Modelo de IA', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Modelo de Inteligência Artificial', fontsize=12, fontweight='bold')

# Adicionar os números exatos por cima de cada barra
for i, v in enumerate(tempos_medios['Tempo_Resposta_ms']):
    ax.text(i, v + (v * 0.02), f"{v:.4f} ms", ha='center', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('grafico_tempo_medio_modelos.png', dpi=300)


# GRÁFICO 2: BOXPLOT DA VARIAÇÃO / ESTABILIDADE
# O Boxplot é ideal para teses porque mostra os outliers (ex: quando um pacote demora imenso a ser processado)
print("📊 A desenhar: Distribuição e Estabilidade (Boxplot)...")
plt.figure(figsize=(12, 7))

sns.boxplot(x='Modelo_IA', y='Tempo_Resposta_ms', data=df, palette='Set2')
plt.title('Variação e Estabilidade da Latência (Boxplot)', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Modelo de Inteligência Artificial', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_boxplot_modelos.png', dpi=300)


# GRÁFICO 3: TEMPO POR TIPO DE ANOMALIA
print("📊 A desenhar: Tempo Médio de Resposta por Classe de Ataque...")
plt.figure(figsize=(14, 7))

# Usamos errorbar=None para não criar linhas de erro confusas nas barras
sns.barplot(x='Classe_Detetada', y='Tempo_Resposta_ms', hue='Modelo_IA', data=df, palette='muted', edgecolor='black', errorbar=None)

plt.title('Tempo Médio de Resposta por Classe de Tráfego', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Tempo de Resposta (ms)', fontsize=12, fontweight='bold')
plt.xlabel('Tipo de Tráfego / Anomalia', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontweight='bold')
plt.legend(title='Modelo Usado', fontsize=11, title_fontsize=12)

plt.tight_layout()
plt.savefig('grafico_tempo_por_classe.png', dpi=300)


# GRÁFICO 4: CONTAGEM DE DETEÇÕES (PRECISÃO)
print("📊 A desenhar: Contagem de Deteções por Classe...")
plt.figure(figsize=(14, 7))

# Contagem das classes agrupadas por modelo
ax4 = sns.countplot(x='Classe_Detetada', hue='Modelo_IA', data=df, palette='Set1', edgecolor='black')

# Adicionar linha indicadora do limite esperado (já que enviámos 10 de cada do Kali)
plt.axhline(y=10, color='red', linestyle='--', linewidth=2, label='Esperado (10 pacotes reais)')

plt.title('Contagem de Deteções por Classe de Tráfego\n(Avaliação de Precisão: O ideal é cada barra ter o valor 10)', fontsize=16, fontweight='bold', pad=15)
plt.ylabel('Número de Pacotes Detetados', fontsize=12, fontweight='bold')
plt.xlabel('Tipo de Tráfego / Anomalia', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontweight='bold')
plt.legend(title='Modelo Usado', fontsize=11, title_fontsize=12)

# Colocar valores no topo das barras
for container in ax4.containers:
    ax4.bar_label(container, padding=3, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_contagem_precisao.png', dpi=300)

print("\n🏁 SUCESSO! Quatro excelentes gráficos académicos foram criados na tua pasta:")
print("  👉 grafico_tempo_medio_modelos.png")
print("  👉 grafico_boxplot_modelos.png")
print("  👉 grafico_tempo_por_classe.png")
print("  👉 grafico_contagem_precisao.png")

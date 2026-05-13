# Simulação de Rede com Mininet

Esta pasta contém o ambiente controlado para testar o sistema de mitigação de ataques utilizando o **Mininet**.

## 🏗️ Topologia da Rede

A simulação cria uma rede simples composta por:
*   **h1 (Atacante):** IP 10.0.0.1
*   **h2 (Vítima/Defesa):** IP 10.0.0.2
*   **s1 (Switch):** Interliga os hosts.

---

## 🚀 Como Executar

Sigue estes passos no teu terminal Linux ou WSL:

### 1. Iniciar a Rede Virtual
Executa o script da topologia:
```bash
sudo python3 topo_mitigacao.py
```
*(Isto abrirá a consola `mininet>`).*

### 2. Abrir os Terminais das Máquinas
Dentro da consola do Mininet, abre os terminais individuais para o atacante e para a vítima:
```bash
mininet> xterm h1 h2
```

### 3. Iniciar a Defesa (no terminal do h2)
No terminal que abriu para o **h2**, inicia o sistema de escuta e mitigação:
```bash
python3 analisa_rede.py
```

### 4. Lançar o Ataque (no terminal do h1)
No terminal que abriu para o **h1**, inicia o disparo de pacotes maliciosos:
```bash
python3 disparar_ataques.py
```

---

## 📊 Visualização de Dados e Gráficos

Após realizares os ataques, o sistema guarda automaticamente os resultados em:
`mininet/dados_apos_ataque/historico_testes_modelos.csv`

Para gerar os gráficos académicos para o teu relatório, navega até à pasta de dados e corre o gerador:
```bash
cd dados_apos_ataque
python3 gerar_graficos_tempos.py
```

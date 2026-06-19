# Simulação de Rede Smart City com IA (Mininet)

Este diretório contém o ambiente de emulação para testar o **Sistema de Prevenção de Intrusões (IPS)** no Edge, utilizando modelos de Machine Learning (ex: XGBoost, LightGBM).

## Topologia da Rede (Arquitetura Empresarial)

A simulação cria uma rede avançada com espelhamento de portas (*Port Mirroring*), composta por:
* **h1 (Atacante / Sensor):** IP `10.0.0.1` - Dispositivo IoT que envia dados (e ataques).
* **r1 (Edge Gateway):** IP `10.0.0.2` - O router que encaminha o tráfego e onde as regras de firewall são aplicadas.
* **ServidorIA (Servidor IDS/IPS):** IP `10.0.0.3` - Servidor dedicado que escuta uma cópia de todo o tráfego do switch e executa o modelo de Inteligência Artificial.
* **s1 (Switch OVS):** Interliga os nós e duplica o tráfego do Gateway para o ServidorIA.

---

## Guia de Execução (Sem XTERM)

Devido às limitações de interface gráfica no WSL (Windows Subsystem for Linux), utilizamos uma abordagem profissional de múltiplos terminais no VS Code.

### 1. Limpar Simulações Anteriores
Antes de iniciar, garante que não há processos do Mininet "presos" na memória:
```bash
sudo mn -c
```

### 2. Iniciar a Topologia
Antes de iniciar, garante que não há processos do Mininet "presos" na memória:
```bash
sudo python3 topo_mitigacao.py
```

### 3. Abrir os Terminais das Máquinas
Dentro da consola do Mininet, abre os terminais individuais para o atacante e para a vítima:
```bash
mininet> xterm h1 h2
```



### 4. Iniciar a Defesa (no terminal do h2)
No terminal que abriu para o **h2**, inicia o sistema de escuta e mitigação:
```bash
python3 analisa_rede.py
```

### 5. Lançar o Ataque (no terminal do h1)
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

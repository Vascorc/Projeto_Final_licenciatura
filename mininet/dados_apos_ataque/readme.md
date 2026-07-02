# Dados Após Ataque (Modo Recolha / Benchmark)

Variante dos scripts de simulação do Mininet (ver `../readme.md` e `../analisa_rede.py`), pensada para correr um **ataque em lote completo** (em vez de uma demonstração interativa) e registar os resultados em CSV para depois gerar gráficos académicos de desempenho.

## 📄 Ficheiros

* **`disparar_ataques.py`** — Versão do disparador de ataques que envia todo o `dataset_validar_treino.csv` (em vez de um ficheiro de ataque avulso) para `10.0.0.2:5005`, incluindo o **número da linha original** (`Packet_ID`) em cada pacote UDP, para depois se poder cruzar cada previsão com o dado real. Velocidade ajustada (`ATRASO = 0.015`) para não perder pacotes.
* **`analisa_rede_sem_blacklist.py`** — Versão do sistema de deteção sem a lógica de blacklist e **sem aplicar `iptables`** (o bloqueio real está desativado), para que todos os pacotes sejam sempre classificados pela IA. Regista cada previsão num buffer em memória e, no final (`Ctrl+C`), grava tudo em `historico_testes_modelos.csv` com colunas `Packet_ID, DataHora, Modelo_IA, IP_Origem, Classe_Detetada, Acao_Tomada, Tempo_Resposta_ms`.
* **`gerar_graficos_tempos.py`** — Cruza `historico_testes_modelos.csv` com `../../analise_network/datasets/dataset_validar_treino.csv` (pelo `Packet_ID`) para saber se cada previsão acertou, e gera vários gráficos académicos: tempo médio de inferência, boxplot de latência, tempo por classe, precisão global e uma matriz de confusão por modelo.
* **`testado_validacao_teste/`** — Resultados de uma execução anterior já guardados (CSV + gráficos `.png`).

## 🚀 Como executar

Requer a topologia Mininet já ativa (ver `../readme.md`). Antes de trocar de modelo, edita `CAMINHO_MODELO`/`CAMINHO_ENCODER` em `analisa_rede_sem_blacklist.py` para apontar para a pasta do modelo desejado (`../../analise_network/modelos/<Modelo>/`).

No terminal do host **h2** (servidor de IA):
```bash
python3 analisa_rede_sem_blacklist.py
```

No terminal do host **h1** (atacante):
```bash
python3 disparar_ataques.py
```

No final da recolha, interrompe o `analisa_rede_sem_blacklist.py` com `Ctrl+C` para forçar a gravação do `historico_testes_modelos.csv`. Depois gera os gráficos:
```bash
python3 gerar_graficos_tempos.py
```

## 🛠️ Dependências

```bash
pip3 install joblib pandas numpy scapy scikit-learn seaborn matplotlib
```

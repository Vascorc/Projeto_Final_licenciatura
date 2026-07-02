# Resultados de uma Execução Anterior

Esta pasta não contém código — guarda os **resultados de uma corrida já feita** do fluxo descrito em `../readme.md` (disparo em lote do `dataset_validar_treino.csv` + `analisa_rede_sem_blacklist.py` + `gerar_graficos_tempos.py`).

## 📄 Ficheiros

* **`historico_testes_modelos.csv`** — Registo pacote a pacote (`Packet_ID`, data/hora, modelo de IA, IP de origem, classe detetada, ação tomada, tempo de resposta em ms) dessa execução.
* **`grafico_tempo_medio_modelos.png`** — Tempo médio de inferência por modelo.
* **`grafico_boxplot_modelos.png`** — Distribuição/estabilidade da latência por modelo.
* **`grafico_tempo_por_classe.png`** — Tempo médio de resposta por tipo de tráfego detetado.
* **`grafico_precisao_modelos.png`** — Accuracy global por modelo.
* **`grafico_matriz_confusao_*.png`** — Uma matriz de confusão por modelo (LightGBM, Random Forest, XGBoost, MLP).

Não há nada para executar aqui — são apenas os outputs já gerados. Para reproduzir estes ficheiros a partir do zero, segue as instruções em `../readme.md`.

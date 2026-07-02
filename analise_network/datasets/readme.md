# Datasets de Rede

Dados de tráfego de rede usados para treinar e validar os modelos de deteção de ataques.

## 📄 Ficheiros

* **`Merged05.csv` … `Merged10.csv`** — Ficheiros brutos de tráfego (grandes) com uma coluna `Label` original que identifica o tipo de tráfego (ex: `BENIGN`, `DDoS`, `Mirai`, `BruteForce`, etc.).
* **`dataset_treino.csv`** — Dataset já balanceado (undersampling, 10 mil amostras por categoria) usado para **treinar** os modelos em `../modelos/*/treinar_network.py`.
* **`dataset_validar_treino.csv`** — Dataset gerado a partir dos ficheiros `Merged06` a `Merged10`, usado para **validar/testar às cegas** os modelos já treinados (scripts `comparar_networks.py` e `comparar_anomalias_especificas.py`).
* **`gerar_dataset_10k.py`** — Script que lê os ficheiros `Merged*.csv`, agrupa o tráfego nas categorias de mitigação (`Normal`, `DDoS-TCP`, `DDoS-UDP/ICMP`, `DoS-TCP`, `DoS-UDP/ICMP`, `Mirai-Botnet`, `BruteForce`, `Spoofing`, `Recon`, `Outros`), faz undersampling a 10.000 amostras por categoria e guarda o resultado em `dataset_validar_treino.csv`.

## 🚀 Como executar

Dentro desta pasta, com os ficheiros `Merged06.csv` a `Merged10.csv` presentes:

```bash
python3 gerar_dataset_10k.py
```

Isto produz (ou substitui) o `dataset_validar_treino.csv`.

## 🛠️ Dependências

```bash
pip3 install pandas
```

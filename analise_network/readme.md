# Análise de Rede (Deteção de Ataques de Rede)

Esta pasta contém todo o trabalho de Machine Learning para a componente de **cibersegurança de rede** do projeto: preparação dos dados, treino de 4 modelos diferentes e comparação dos seus resultados. É o "cérebro" que depois é usado em tempo real pela simulação em `../mininet/`.

## 📂 Estrutura

* **`datasets/`** — CSVs brutos (`Merged05.csv` a `Merged10.csv`), o script que gera o dataset de treino balanceado, e os datasets já processados (`dataset_treino.csv`, `dataset_validar_treino.csv`).
* **`modelos/`** — Um subdiretório por algoritmo (`LightGBM/`, `XGBoost/`, `Random Forest/`, `Multi-Layer_Perceptron/`), cada um com o seu script de treino e os ficheiros `.pkl` (modelo + encoder + scaler) já treinados. Também tem os scripts que comparam os 4 modelos entre si.

Consulta o `readme.md` dentro de cada subpasta para instruções específicas.

## 🔁 Fluxo de trabalho típico

1. `datasets/gerar_dataset_10k.py` → gera `dataset_validar_treino.csv` a partir dos ficheiros `Merged*.csv`.
2. Dentro de cada pasta de `modelos/`, corre-se `treinar_network.py` para treinar e guardar esse modelo.
3. `modelos/comparar_networks.py` e `modelos/comparar_anomalias_especificas.py` avaliam os 4 modelos treinados contra `dataset_validar_treino.csv` e geram gráficos comparativos.

## 🛠️ Dependências

```bash
pip3 install pandas numpy scikit-learn lightgbm xgboost joblib matplotlib
```

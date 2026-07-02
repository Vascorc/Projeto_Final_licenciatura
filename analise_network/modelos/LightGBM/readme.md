# Modelo LightGBM

Treino do classificador **LightGBM** (multi-classe) para deteção de ataques de rede.

## 📄 Ficheiros

* **`treinar_network.py`** — Lê `../../datasets/dataset_treino.csv`, agrupa o `Label` original nas categorias de mitigação, codifica as classes (`LabelEncoder`), limpa valores infinitos/NaN, divide 80/20 treino/teste e treina um `LGBMClassifier(n_estimators=100)`.
* **`modelo_ciberseguranca_lgbm.pkl`** — Modelo já treinado (gerado pelo script acima).
* **`label_encoder_categorias_lgbm.pkl`** — `LabelEncoder` que traduz as classes previstas (números) de volta para os nomes das categorias (ex: `DDoS-TCP`).

## 🚀 Como executar

```bash
python3 treinar_network.py
```

Corre a partir desta pasta — o script assume que `dataset_treino.csv` está em `../../datasets/`. No final gera/substitui os dois ficheiros `.pkl`.

## 🛠️ Dependências

```bash
pip3 install pandas numpy scikit-learn lightgbm joblib
```

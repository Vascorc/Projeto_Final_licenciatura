# Modelo Multi-Layer Perceptron (MLP)

Treino da **Rede Neuronal MLP** para deteção de ataques de rede. Segundo as notas do projeto (`../../../Suportes para defesa/notas defesa.txt`), este foi o modelo que se revelou a solução ótima no trabalho.

## 📄 Ficheiros

* **`treinar_network.py`** — Lê `../../datasets/dataset_treino.csv`, agrupa o `Label` original nas categorias de mitigação, codifica as classes (`LabelEncoder`), limpa valores infinitos/NaN, divide 80/20 treino/teste, **normaliza os dados com `StandardScaler`** (só ajustado nos dados de treino) e treina um `MLPClassifier(hidden_layer_sizes=(50,), max_iter=100, early_stopping=True)`.
* **`modelo_ciberseguranca_mlp.pkl`** — Modelo já treinado (gerado pelo script acima).
* **`label_encoder_categorias_mlp.pkl`** — `LabelEncoder` que traduz as classes previstas (números) de volta para os nomes das categorias.
* **`scaler_ciberseguranca_mlp.pkl`** — `StandardScaler` usado para normalizar os dados antes de os passar ao modelo (necessário também em produção, antes de qualquer previsão).

## 🚀 Como executar

```bash
python3 treinar_network.py
```

Corre a partir desta pasta — o script assume que `dataset_treino.csv` está em `../../datasets/`. No final gera/substitui os três ficheiros `.pkl`.

## 🛠️ Dependências

```bash
pip3 install pandas numpy scikit-learn joblib
```

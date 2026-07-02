# Modelos de Deteção de Ataques de Rede

Contém os 4 modelos de Machine Learning treinados para classificar tráfego de rede (Normal vs. vários tipos de ataque: DDoS, DoS, Mirai-Botnet, BruteForce, Spoofing, Recon) e os scripts que os comparam entre si.

## 📂 Subpastas

* **`LightGBM/`**, **`XGBoost/`**, **`Random Forest/`**, **`Multi-Layer_Perceptron/`** — Cada uma contém o script de treino (`treinar_network.py`) desse algoritmo e os ficheiros `.pkl` gerados (modelo, label encoder e, no caso do MLP, o scaler). Ver o `readme.md` de cada uma.

## 📄 Scripts de comparação

* **`comparar_networks.py`** — Carrega os 4 modelos treinados, testa-os contra `../datasets/dataset_validar_treino.csv` (teste cego / dados nunca vistos no treino) e gera:
  * `grafico_teste_cego_global.png` — Accuracy e F1-Score globais dos 4 modelos.
  * `grafico_teste_cego_anomalias.png` — Recall (taxa de acerto) por categoria de tráfego, para cada modelo.
* **`comparar_anomalias_especificas.py`** — Mesma lógica, mas foca-se em 3 categorias específicas (`Normal`, `BruteForce`, `Recon`) e gera um gráfico individual para cada uma: `grafico_teste_cego_normal.png`, `grafico_teste_cego_bruteforce.png`, `grafico_teste_cego_recon.png`.

Os `.png` já presentes nesta pasta são os gráficos gerados numa execução anterior.

## 🚀 Como executar

Pré-requisito: os 4 modelos já têm de estar treinados (ver `readme.md` de cada subpasta) e o ficheiro `../datasets/dataset_validar_treino.csv` tem de existir.

```bash
cd LightGBM && python3 treinar_network.py && cd ..
cd XGBoost && python3 treinar_network.py && cd ..
cd "Random Forest" && python3 treinar_network.py && cd ..
cd Multi-Layer_Perceptron && python3 treinar_network.py && cd ..

python3 comparar_networks.py
python3 comparar_anomalias_especificas.py
```

## 🛠️ Dependências

```bash
pip3 install pandas numpy scikit-learn joblib matplotlib
```

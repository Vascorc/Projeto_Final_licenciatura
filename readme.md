# Sistema de Mitigação no Edge (Projeto Final de Licenciatura)

Este projeto implementa um sistema de firewall inteligente com base em modelos de Machine Learning (LightGBM, XGBoost, Random Forest e MLP). O sistema monitoriza o tráfego de rede em tempo real e aplica regras de mitigação (bloqueio) através de `iptables` caso detete anomalias.

## 📂 Estrutura do Projeto

*   **`mininet/`**: Contém todo o ambiente de simulação e os scripts de execução em tempo real.
*   **`analise_network/modelos/`**: Contém os cérebros da IA treinados (`.pkl`).
*   **`analise_network/datasets/`**: Ficheiros CSV utilizados para treino e disparos de teste.

## 🚀 Como Executar a Simulação

Toda a lógica de execução e simulação foi centralizada na pasta **`mininet/`**.

Para instruções detalhadas de como subir a rede virtual, correr os ataques e visualizar os gráficos de mitigação, consulta o README específico:
👉 **[Instruções da Simulação (Mininet)](./mininet/readme.md)**

## 🛠️ Instalação das Dependências

Abre o terminal no teu ambiente Linux ou WSL e instala as bibliotecas necessárias:

```bash
pip3 install joblib pandas numpy scapy lightgbm xgboost scikit-learn seaborn matplotlib
```

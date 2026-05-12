# Sistema de Mitigação no Edge (Projeto Final de Licenciatura)

Este projeto implementa um sistema de firewall inteligente com base num modelo de Machine Learning (LightGBM). O script monitoriza o tráfego de rede em tempo real e aplica regras de mitigação (bloqueio) através de `iptables` caso detete anomalias (como ataques DDoS, DoS, BruteForce, Mirai-Botnet, entre outros).

## ⚠️ Pré-requisitos Importantes

Devido à utilização de ferramentas específicas para manipulação de pacotes de rede e firewall, **este script DEVE ser executado num ambiente Linux**.

Se estiveres a utilizar Windows, é **altamente recomendável** utilizar o **WSL (Windows Subsystem for Linux)** (preferencialmente WSL2).
O script interage nativamente com a interface de rede `eth0` (padrão do WSL/Linux) e comandos de `iptables` que não existem no Windows.

## 🛠️ Instalação das Dependências

Para que o script de Machine Learning funcione e consiga ler os modelos previamente treinados (`.pkl`), é necessário instalar algumas bibliotecas Python.

Abre o terminal no teu ambiente Linux ou WSL, navega até à pasta do projeto, instala as dependências:

1. **Caso não tenhas o `pip` instalado:**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   ```

2. **Instala as bibliotecas necessárias:**
   ```bash
   pip3 install joblib pandas numpy scapy lightgbm xgboost scikit-learn seaborn matplotlib
   ```
   *(Nota: O `xgboost` serve para usar o respetivo modelo de IA, enquanto o `seaborn` e `matplotlib` são necessários para correr o script que gera os gráficos académicos. Se o sistema Linux/WSL te pedir para criares um ambiente virtual, podes optar por fazê-lo ou adicionar `--break-system-packages` ao comando acima).*

## 🚀 Como Executar

O script precisa de interagir diretamente com a placa de rede (modo de escuta) e realizar alterações de segurança no sistema (regras de firewall). Por este motivo, tem de ser **obrigatoriamente executado com privilégios de Administrador (`root`)**.

Para iniciar o sistema de mitigação, corre o seguinte comando:

```bash
sudo python3 analisa_rede.py
```

O sistema ficará ativo à escuta da rede e informará no terminal caso detete algum tráfego anómalo, aplicando a devida mitigação através do IP atacante.

#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os

def meuProjetoTopo():
    "Topologia Profissional com Servidor IDS e Port Mirroring"
    
    net = Mininet( controller=None, switch=OVSSwitch )

    info( '*** Adicionando os hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )       # Atacante / Sensor
    r1 = net.addHost( 'r1', ip='10.0.0.2' )       # Edge Gateway
    h2 = net.addHost( 'h2', ip='10.0.0.3' )       # Servidor Inteligência Artificial (antigo ServidorIA)

    info( '*** Adicionando o switch\n' )
    s1 = net.addSwitch( 's1', failMode='standalone' )

    info( '*** Criando os links\n' )
    # Ao ligarmos os nós desta forma, o Mininet cria automaticamente as interfaces h1-eth0, r1-eth0 e h2-eth0
    net.addLink( h1, s1, port2=1 )       # h1 ligado na porta 1 do switch
    net.addLink( r1, s1, port2=2 )       # r1 ligado na porta 2 do switch
    net.addLink( h2, s1, port2=3 )       # h2 ligado na porta 3 do switch

    info( '*** Iniciando a rede\n' )
    net.start()

    info( '*** Configurando Port Mirroring (Cópia de Tráfego)...\n' )
    # Extraímos o UUID da porta s1-eth3 primeiro, e depois criamos o espelho
    comando_mirror = 'ovs-vsctl -- set Bridge s1 mirrors=@m -- --id=@m create Mirror name=espelho select-all=true output-port=$(ovs-vsctl get port s1-eth3 _uuid)'
    os.system(comando_mirror)

    info( '*** Rede Pronta!\n' )
    info( 'DICA 1: Abre os terminais com: xterm h1 h2\n' )
    info( 'DICA 2: Na janela do h2, corre o analisa_rede.py\n' )
    info( 'DICA 3: Na janela do h1, lança o ataque com disparar_ataques.py\n' )
    
    CLI( net )

    info( '*** Parando a rede\n' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    meuProjetoTopo()
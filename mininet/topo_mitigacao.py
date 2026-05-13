#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def meuProjetoTopo():
    "Cria uma rede simples para testes de mitigação."
    
    # Criamos a rede sem controlador
    net = Mininet( controller=None, switch=OVSSwitch )

    info( '*** Adicionando os hosts\n' )
    # h1 é o atacante
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    # h2 é o servidor/defesa
    h2 = net.addHost( 'h2', ip='10.0.0.2' )

    info( '*** Adicionando o switch\n' )
    s1 = net.addSwitch( 's1', failMode='standalone' )

    info( '*** Criando os links\n' )
    net.addLink( h1, s1 )
    net.addLink( h2, s1 )

    info( '*** Iniciando a rede\n' )
    net.start()

    info( '*** Rede Pronta!\n' )
    info( 'DICA: Para testar, usa h1 para atacar e h2 para defender.\n' )
    
    # Abre a consola do Mininet para dar comandos manuais
    CLI( net )

    info( '*** Parando a rede\n' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    meuProjetoTopo()

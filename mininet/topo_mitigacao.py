from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os

def meuProjetoTopo():
    "Topologia Profissional com Servidor IDS e Port Mirroring"
    
    net = Mininet( controller=None, switch=OVSSwitch )

    info( '*** Adicionando os hosts\n' )
    h1 = net.addHost( 'Atacante', ip='10.0.0.1' )
    r1 = net.addHost( 'Gateway', ip='10.0.0.2' )
    
    # O Servidor Dedicado à Inteligência Artificial
    serv_ia = net.addHost( 'ServidorIA', ip='10.0.0.3' )

    info( '*** Adicionando o switch\n' )
    s1 = net.addSwitch( 's1', failMode='standalone' )

    info( '*** Criando os links (Fixando portas para o espelhamento)\n' )
    net.addLink( h1, s1, port2=1 )       # h1 ligado na porta 1 do switch
    net.addLink( r1, s1, port2=2 )       # Gateway ligado na porta 2 do switch
    net.addLink( serv_ia, s1, port2=3 )  # ServidorIA ligado na porta 3 do switch

    info( '*** Iniciando a rede\n' )
    net.start()

    info( '*** Configurando Port Mirroring (Cópia de Tráfego)...\n' )
    # Este comando mágico diz ao Switch OVS para copiar o tráfego e enviá-lo também para a porta 3 (ServidorIA)
    comando_mirror = 'ovs-vsctl -- set Bridge s1 mirrors=@m -- --id=@m create Mirror name=espelho select-all=true output-port=s1-eth3'
    os.system(comando_mirror)

    info( '*** Rede Pronta!\n' )
    info( 'DICA 1: Lança o teu script de IA no ServidorIA.\n' )
    info( 'DICA 2: Usa o h1 para atacar o Gateway (10.0.0.2).\n' )
    
    CLI( net )

    info( '*** Parando a rede\n' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    meuProjetoTopo()
from mininet.topo import Topo
from mininet.link import TCLink

class FatTreeTopo(Topo):
    def __init__(self):
        # Khởi tạo Topology
        Topo.__init__(self)

        # Tạo các switch
        core_switch = self.addSwitch('s1')
        agg_switch1 = self.addSwitch('s2')
        agg_switch2 = self.addSwitch('s3')
        edge_switch1 = self.addSwitch('s4')
        edge_switch2 = self.addSwitch('s5')

        # Tạo các host
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')

        # Kết nối core switch tới các aggregation switch
        self.addLink(core_switch, agg_switch1, cls=TCLink, bw=10)
        self.addLink(core_switch, agg_switch2, cls=TCLink, bw=10)

        # Kết nối aggregation switch tới edge switch
        self.addLink(agg_switch1, edge_switch1, cls=TCLink, bw=10)
        self.addLink(agg_switch1, edge_switch2, cls=TCLink, bw=10)
        self.addLink(agg_switch2, edge_switch1, cls=TCLink, bw=10)
        self.addLink(agg_switch2, edge_switch2, cls=TCLink, bw=10)

        # Kết nối edge switch tới các host
        self.addLink(edge_switch1, h1, cls=TCLink, bw=10)
        self.addLink(edge_switch1, h2, cls=TCLink, bw=10)
        self.addLink(edge_switch2, h3, cls=TCLink, bw=10)
        self.addLink(edge_switch2, h4, cls=TCLink, bw=10)

topos = {'mytopo': (lambda: FatTreeTopo())}

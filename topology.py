from mininet.topo import Topo

class FatTreeTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Add core, aggregation, and edge switches
        coreSwitch = self.addSwitch('s1')
        aggSwitch1 = self.addSwitch('s2')
        aggSwitch2 = self.addSwitch('s3')
        edgeSwitch1 = self.addSwitch('s4')
        edgeSwitch2 = self.addSwitch('s5')

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Add links
        self.addLink(coreSwitch, aggSwitch1)
        self.addLink(coreSwitch, aggSwitch2)
        self.addLink(aggSwitch1, edgeSwitch1)
        self.addLink(aggSwitch1, edgeSwitch2)
        self.addLink(aggSwitch2, edgeSwitch1)
        self.addLink(aggSwitch2, edgeSwitch2)

        # Host connections
        self.addLink(edgeSwitch1, h1)
        self.addLink(edgeSwitch1, h2)
        self.addLink(edgeSwitch2, h3)
        self.addLink(edgeSwitch2, h4)

topo = FatTreeTopo()

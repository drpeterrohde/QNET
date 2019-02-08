import QNET
import os

os.system('clear')
QNET.info()

net = QNET.Network()

node1 = QNET.Node('Alice')
node2 = QNET.Node('Bob')
chan1 = QNET.Channel()
chan2 = QNET.Channel()

node1.connectTo(node2, chan1)
node2.connectTo(node1, chan2)

net.addNode(node1)
net.addNode(node2)
net.addChannel(chan1)
net.addChannel(chan2)

g = QNET.Graph([node1, node2])
print(g.adjacencyMatrix)
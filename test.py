import QNET
import os

os.system('clear')
QNET.info()

net = QNET.Network()

node1 = QNET.Node()
node2 = QNET.Node()
chan1 = QNET.Channel()
chan2 = QNET.Channel()

node1.channels.append(chan1)
node2.channels.append(chan2)

chan1.source = node1
chan1.dest = node2
chan2.source = node2
chan2.dest = node1

net.addNode(node1)
net.addNode(node2)
net.addChannel(chan1)
net.addChannel(chan2)

g = QNET.Graph([1,2,3,4])
print(g.adjacencyMatrix)
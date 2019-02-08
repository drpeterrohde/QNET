import QNET
import os

os.system('clear')
QNET.info()

net = QNET.Network()

node1 = QNET.Node('Alice')
node2 = QNET.Node('Bob')
chan1 = QNET.Channel()
chan2 = QNET.Channel()
chan1.cost.costs = {'loss': 100}
chan1.source = node1
chan1.dest = node2
chan2.cost.costs = {'loss': 200}
chan2.source = node2
chan2.dest = node1

node1.connectTo(node2, chan1)
node2.connectTo(node1, chan2)

net.addNode(node1)
net.addNode(node2)
net.addChannel(chan1)
net.addChannel(chan2)

g = QNET.Graph([node1, node2])

print('adj = ', g.adjacencyMatrix)
print()
A, B = g.shortestPath(1,0)
print('shortest path = ')
print(A)
print(B)

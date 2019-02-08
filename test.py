import QNET
import os

os.system('clear')
QNET.info()

net = QNET.Network()

node1 = QNET.Node('Alice')
node2 = QNET.Node('Bob')
node3 = QNET.Node('Charlie')
chan1 = QNET.Channel()
chan2 = QNET.Channel()
chan3 = QNET.Channel()
chan1.cost.costs = {'loss': 100}
chan1.source = node1
chan1.dest = node2
chan2.cost.costs = {'loss': 200}
chan2.source = node2
chan2.dest = node1
chan3.cost.costs = {'loss': 1000}
chan3.source = node3
chan2.dest = node1

node1.connectTo(node2, chan1)
node2.connectTo(node1, chan2)
node3.connectTo(node1, chan3)

net.addNode(node1)
net.addNode(node2)
net.addNode(node3)
net.addChannel(chan1)
net.addChannel(chan2)
net.addChannel(chan3)

g = QNET.Graph([node1, node2, node3])

print('adj = ', g.adjacencyMatrix)
print()
A, B = g.shortestPath(0,2)
print('shortest path = ')
print(A)
print(B)

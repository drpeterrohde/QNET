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
chan2.cost.costs = {'loss': 200}
chan3.cost.costs = {'loss': 1000}

node1.connectTo(node2, chan1)
node2.connectTo(node3, chan2)
node3.connectTo(node1, chan3)

net.addNode(node1)
net.addNode(node2)
net.addNode(node3)
net.addChannel(chan1)
net.addChannel(chan2)
net.addChannel(chan3)

g = QNET.Graph([node1, node2, node3])

print('adj = ')
print(g.adjacencyMatrix)
print()

[dist, pred] = g.shortestPath(0,2)
print('distances = ')
print(dist)
print()
print('pred = ')
print(pred)

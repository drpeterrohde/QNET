import QNET
import os

os.system('clear')
QNET.info()

net = QNET.Network()

node1 = QNET.Node('Alice')
node2 = QNET.Node('Bob')
node3 = QNET.Node('Charlie')
node4 = QNET.Node('Dylan')

chan1 = node1.connectTo(node2)
chan2 = node2.connectTo(node3)
chan3 = node2.connectTo(node4)
chan4 = node4.connectTo(node1)

chan1.setCost('loss', 100)
chan2.setCost('loss', 200)
chan3.setCost('loss', 1000)
chan4.setCost('loss', 5000)

net.addNode(node1)
net.addNode(node2)
net.addNode(node3)
net.addNode(node4)
net.addChannel(chan1)
net.addChannel(chan2)
net.addChannel(chan3)
net.addChannel(chan4)

g = QNET.Graph([node1, node2, node3, node4])

print('adj = ')
print(g.adjacencyMatrix)
print()

[dist, pred] = g.shortestPath(0,3)
print('distances = ')
print(dist)
print()
print('pred = ')
print(pred)

import matplotlib.animation as animation
# Plot functions
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d

import QNET
# Qnet Graph
from Graph2 import X as X2

# Note, widgets only work with jupyter notebook
# %matplotlib widget

## This function takes a Qnet graph and returns a figure
def Qnet3dPlot(Q):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Note widget requires external packkage jupyter matplotlib
    # %matplotlib widget

    for node in X2.nodes:
        x = node.coords[0]
        y = node.coords[1]
        z = node.coords[2]

        # Dictionary between colours and node types
        qnode_color = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}

        ax.scatter(x, y, z, c=qnode_color[type(node)], marker='o')
        ax.text(x, y, z, '%s' % node.name, size=12, zorder=1)

        # Todo: Figure out how to offset text.

    for edge in X2.edges:
        xs = [edge[0].coords[0], edge[1].coords[0]]
        ys = [edge[0].coords[1], edge[1].coords[1]]
        zs = [edge[0].coords[2], edge[1].coords[2]]

        # TODO: Set custom line styles depending on which nodes are being connected
        # TODO: Label lines with costs

        if (isinstance(edge[0], QNET.Satellite) or isinstance(edge[1], QNET.Satellite)):
            line = art3d.Line3D(xs, ys, zs, linestyle='--')

        else:
            line = art3d.Line3D(xs, ys, zs)

        ax.add_line(line)

    return fig

def QnetAnimation(Q, dt):
    # TODO:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Setting the axes properties
    ax.set_xlim3d([0.0, 1.0])
    ax.set_xlabel('X')

    ax.set_ylim3d([0.0, 1.0])
    ax.set_ylabel('Y')

    ax.set_zlim3d([0.0, 1.0])
    ax.set_zlabel('Z')

    ax.set_title('3D Test')

    # Creating the Animation object
    animation.FuncAnimation(Qnet3dPlot(Q), func=Q.update, frames=500,
                                       fargs=(dt), interval=50, blit=False)

    plt.show()

QnetAnimation(X2, dt=0.01)
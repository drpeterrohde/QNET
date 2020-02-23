import QNET
from Node import Node
from Node import Satellite
from Channel import Channel
from reader import readData
import copy

# TODO:
# Tidy up so we only have to import QNET
#

class Network:
    def __init__(self, name = 'QNET Network'):
        self.name = name
        self.nodes = []
        self.nodeNames = []
        self.channels = []

    def __str__(self):
        return('Network: ' + self.name +
            '\n Nodes: ' + str(len(self.nodes)) + ', Channels: ' + str(len(self.channels)))
    
    
    ######### BASICS ##########

    def addNode(self, node):
        self.nodes.append(node)
        self.nodeNames.append(node.name)
       
    def addChannel(self, channel):
        self.channels.append(channel)
    
    
    #### USELESS FUNCTION? ####
    # Given a name in self.nodeNames, gets the node
    # Else returns none
    def getNode(self, name):
        if name in self.nodeNames:
            for node in self.nodes:
                if name == node.name:
                    return node
        else:
            return None
    
    
    ####### PARSERS ######
        
    # Reads in nodes from a specified file and adds them to network
    def readNodes(self, file):
        nodeData = readData(file)
        
        # nodeData.columns is a list of column names
        # It is NOT a list of values
        
        # Assume the names of nodes are in first column.
        name = nodeData.columns[0]
        
        # Assume Coordinates of nodes are in second and third columns
        lat = nodeData.columns[1]
        long = nodeData.columns[2]
        
        
        # Initialise nodes and add them to the network
        
        i = 0
        while (i < len(nodeData[name])):
            
            # Pay close attention here! Difficult pd syntax
            newName = nodeData[name][i]
            newCoords = [ nodeData[lat][i], nodeData[long][i] ]
            
            newNode = Node(newName, newCoords) 
            
            i += 1
            self.addNode(newNode)
        
        """
        for newNode in nodeData[name]:
            newNode = Node(newNode)
        """
            
            # self.nodes.append(newNode)
    
    def readChannels(self, file):
        edgeData = readData(file)
        
        # Assume source and destination are in the first two columns
        source = edgeData.columns[0]
        destination = edgeData.columns[1]
        
        i = 0
        row_count = edgeData.shape[0]
        while (i < row_count):
            # Get names
            sourceName = edgeData.at[i, source]
            destName = edgeData.at[i, destination]
            
            # Get sourceNode from sourceName: If node doesn't exist, create it
            sourceNode = self.getNode(sourceName)
            if (sourceNode == None):
                sourceNode = Node(sourceName)
                self.addNode(sourceNode)
            
            # Get destNode from destName: If node doesn't exist, create it
            destNode = self.getNode(destName)
            if (destNode == None):
                destNode = Node(destName)
                self.addNode(destNode)
            
            # Initialise new channel
            newChannel = Channel(source = sourceNode, dest = destNode)
            self.channels.append(newChannel)
                
            # Update channels attributes within source and dest            
            sourceNode.connectTo(destNode)
            
            i += 1
    
    
    ############ PRINTING ##############
    
    
    # Prints list of nodes and their coordinates in network
    def printNodes(self):
        print(f"List of nodes in {self.name}:")
        for node in self.nodes:
            print("Name: " + node.name)
            print(f"Coordinates: lat[{node.coords[0]}] long[{node.coords[1]}]")
            print('\n')
    

    def printChannels(self, costType = None):
        if costType != None:
            print(f"List of channels in {self.name}:")
            for channel in self.channels:
            
                sourceNode = channel.source
                destNode = channel.dest
                cost = channel.cost.costs[costType] 
                print(sourceNode.name + ' <-> ' + destNode.name + f' -- {costType} == {cost}')
        else:
            print(f"List of channels in {self.name}:")
            for channel in self.channels:
                sourceNode = channel.source
                destNode = channel.dest
                print(sourceNode.name + ' <-> ' + destNode.name)
    
    
    
    
    ############ NETWORK UPDATING ##############
    
    
    # Update satellite position given timestep
    def updateSatPos(self, dt):
        for node in self.nodes:
            if node.nodeType == 'satellite':
                node.posUpdate(dt)
    
    # Update all satellite channels
    def updateSatChannels(self):
        for node in self.nodes:                        
            if node.nodeType == 'satellite':
                node.updateChannels()
            
    # Update all time dependent elements in network
    
    def updateAll(self, dt):
        
        ### DEBUG ###
        self.updateSatPos(dt)
        self.updateSatChannels()
    
    
    # Distribute cost from swapper node to adjacent channels
    def swap(self):
        for node in self.nodes:
            if isinstance(node, QNET.Swapper):
                node.distribute('loss')
    
    # Inverse of N.swap()            
    def unswap(self):
        for node in self.nodes:
            if isinstance(node, QNET.Swapper):
                node.undistribute('loss')
    

    ########## PATH FETCHING AND MANIPULATION #########
    
    # Given a path of channels, prints the pathCost
    def pathCost(self, chanPath, costType):
        totalCost = 0
        for channel in chanPath:
            totalCost += channel.cost.costs[costType]
        return totalCost
    
    # getPathFromList constructs a list of nodes from network N specified by a List
    # Useful for obtaining paths, however it does NOT check if the path is valid
    # Will warn user if one or more nodes in list does not exist in N.
    def getNodePathFromList(self, List):
        nodes = []
        for name in List:
            nodeExists = False
            for node in self.nodes:
                if node.name == name:
                    nodes.append(node)
                    nodeExists = True
            if nodeExists == False:
                print("Warning! One or more nodes in list does not exist!")
        return nodes
    
    
    # Given nodeList, returns chanPath
    def getChanPathFromList(self, nodeList):
        path = self.getNodePathFromList(nodeList)
        pathChannels = []
        length = len(path)
        i = 0
        
        while (i < length - 1):
            sourceNode = path[i]
            destNode = path[i+1]
            
            for channel in sourceNode.channels:
                if channel.source.name == sourceNode.name and channel.dest.name == destNode.name:
                    pathChannels.append(channel)
                elif channel.source.name == destNode.name and channel.dest.name == sourceNode.name:
                    pathChannels.append(channel)
            i += 1
        return pathChannels
        
        
            
import QNET

allCostVectors = []

class CostVector:
    
    def __init__(self, costDict = {'loss': 0.0}):
        self.costDict = costDict

    def __str__(self):
        return(f'Cost vector: {self.costDict}')

    # TODO:
    # Find out difference between static and dynamic methods for updating
    @staticmethod
    def reformat():
        keys = []

        for vector in QNET.CostVector.allCostVectors:
            keys += vector.costDict.keys()
        uniqueKeys = list(set(keys))

        for vector in QNET.CostVector.allCostVectors:
            for key in uniqueKeys:
                if key not in vector.costDict.keys():
                    vector.costDict[key] = 0

    @staticmethod   
    def add(costVectors):
        sum = QNET.CostVector()

        for vector in costVectors:
            for key in vector.costDict.keys():
                sum.costDict[key] += vector[key]

        return(sum)
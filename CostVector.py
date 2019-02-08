import QNET

class CostVector:
    allCostVectors = []

    def __init__(self, costs = {}):
        self.costs = costs
        QNET.CostVector.allCostVectors.append(self)
        QNET.CostVector.reformat()

    def __str__(self):
        return('Cost vector: ' + str(self.costs))
    
    @staticmethod
    def reformat():
        keys = []

        for vector in QNET.CostVector.allCostVectors:
            keys.append(vector.keys())
        uniqueKeys = list(set(keys))

        for vector in QNET.CostVector.allCostVectors:
            for key in uniqueKeys:
                if key not in vector.costs:
                    vector.costs[key] = 0
        
    @staticmethod
    def add(costVectors):
        sum = QNET.CostVector()

        for vector in costVectors:
            for key in vector.costs.keys():
                sum.costs[key] += vector[key]

        return(sum)

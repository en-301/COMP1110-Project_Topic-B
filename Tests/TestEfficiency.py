import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Modules.Core import *
from Modules.PathManager import *

from GraphManager import InputNumber

import random
import heapq
import math

def GenerateGraph(numNodes: int, numEdges: int, avgOutDegree: int):
    numNodes = max(1, numNodes)
    numEdges = min(numEdges, numNodes * (numNodes - 1))
    avgOutDegree = min(avgOutDegree, numNodes - 1)

    graph = AdjList(numNodes)

    for i in range(numNodes):
        graph.graph[i] = set()  # in case of empty graph, the source node is included
    if (numEdges == 0) or (numNodes == 1): return graph

    nodeHeap = []
    activeNodes = [i for i in range(numNodes)]
    __valMax = max(EPSILON, 1e4 / numEdges)

    def __Eval(outDeg):
        res = (outDeg + 2) ** (0.5 + random.random() * 2)
        # print(f"{outDeg}->{res}") # debug output
        return res

    for i in range(numNodes):
        # introduce a random number (first one) as weighted priority
        heapq.heappush(nodeHeap, (__Eval(0), 0, i))

    edgesAdded = 0
    tmpAdjList = [set() for i in range(numNodes)]

    while nodeHeap and edgesAdded < numEdges:
        _, deg, source = heapq.heappop(nodeHeap)

        # if this source node reaches out degre limit:
        # do not add back the node
        if deg >= avgOutDegree:
            continue

        # skip duplicate nodes (itself and existing destinations)
        to = random.randint(0, numNodes - 1)
        while (to in tmpAdjList[source]) or (to == source):
            to = (to + 1) % numNodes
        
        tmpAdjList[source].add(to)
        edgesAdded += 1
        deg += 1
        # after successful graph addition, push source back into the heap
        heapq.heappush(nodeHeap, (__Eval(deg), deg, source))

    for source in range(numNodes):
        for to in tmpAdjList[source]:
            time = random.random() * __valMax
            cost = random.random() * __valMax
            comfort = random.random()
            graph.AddEdge(Edge(source, to, time, cost, comfort))

    return graph, tmpAdjList

if __name__ == "__main__":
    numNodes  = InputNumber(
        "Input number of nodes of test graphs (2-10000): ",            2,        10000,  True)
    numEdges  = InputNumber(
        f"Input number of edges of test graphs ({numNodes}-100000): ", numNodes, 100000, True)
    numDegree = InputNumber(
        "Input number of maximum out degrees per node (1-10): ",       1,        10,     True)
    numTests  = InputNumber("Input number of tests (1-300): ",         1,        300,    True)
    outputDir = input("Input log directory (leave blank if none): ").strip()

    import time
    
    elapsedTime = []
    for testRoundNum in range(numTests):
        graph, adjList = GenerateGraph(numNodes, numEdges, numDegree)
        sourceNode = max(enumerate(adjList), key=lambda item: len(item[1]))[0]

        __timerStart = time.perf_counter()
        Search(graph, WeightsExp.sortByTime, sourceNode, (sourceNode + 1e5 + 3) % numNodes, 5)
        __elapsedTime = time.perf_counter() - __timerStart
        print(f"Query {testRoundNum + 1} finished in {(__elapsedTime * 1000):.4f} milliseconds")
        elapsedTime.append(__elapsedTime)

    if len(outputDir) > 0:
        import os
        outputPath = os.path.join("./Analysis/", outputDir)
        outputDir = os.path.dirname(outputPath)

        if outputDir and not os.path.exists(outputDir):
            os.makedirs(outputDir)
        with open(outputPath, "w") as outputFile:
            for t in elapsedTime: outputFile.write(str(t) + ",\n")
        print(f"Test results written to {outputPath}")

    print(f"Average execution time across {numTests} rounds:", end=" ")
    print(f"{sum(elapsedTime) / len(elapsedTime):.7f} seconds")


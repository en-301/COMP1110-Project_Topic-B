EPSILON = 1e-4

class Weights:
    def __init__(self, timeWeight: float, costWeight: float, comfortWeight: float):
        self.wtime = timeWeight
        self.wcost = costWeight
        self.wcomfort = comfortWeight
    def Eval(self, edge):
        return max(0, self.wtime * edge.time + self.wcost * edge.cost - self.wcomfort * edge.comfort)

class Edge:
    def __init__(self, sourceNode, targetNode,
                 travelTime: float, routeCost: float, comfortIndex: float, customInfo = None):
        self.source = sourceNode
        self.to = targetNode
        self.time = travelTime
        self.cost = routeCost
        self.comfort = comfortIndex
        self.customData = customInfo if customInfo else {}
    def __eq__(self, other):
        return (
            self.to == other.to and
            abs(self.time - other.time) < EPSILON and
            abs(self.cost - other.cost) < EPSILON and
            abs(self.comfort - other.comfort) < EPSILON
        )
    def __hash__(self):
        return hash((self.to, round(self.time, 4), round(self.cost, 4), round(self.comfort, 4)))
    def __str__(self):
        customDataList = []
        if len(self.customData) > 0:
            for key in self.customData: customDataList.append(self.customData[key])
        return f"[{", ".join(customDataList)}] {self.source} -> {self.to} " + \
               f"({self.time:.0f} min, {self.cost:<.2f} HKD, comfort index {(self.comfort * 10):.0f}/10)"


class AdjList:
    def __init__(self, numNodes: int):
        self.n = numNodes
        self.graph = {}
        self.nodes = set()
    
    def AddEdge(self, edge: Edge):
        self.nodes.add(edge.to)
        
        if edge.source in self.graph:
            self.graph[edge.source].add(edge)
        else:
            self.graph[edge.source] = { edge }
        if edge.to not in self.graph:
            self.graph[edge.to] = set()

        self.nodes.update((edge.source, edge.to))
        self.n = len(self.nodes)


    def AddEdgeBidirectional(self, edge: Edge):
        self.AddEdge(edge)
        edgeReverse = Edge(edge.to, edge.source, edge.time, edge.cost, edge.comfort, edge.customData)
        self.AddEdge(edgeReverse)


import math

Weights.weightBase = Weights(.40, .35, .25)
class WeightsExp(Weights):
    def Eval(self, edge):
        return (
            (max(0, self.wtime * edge.time) + max(0, self.wcost * edge.cost)) *
            math.exp(-max(0, self.wcomfort) * edge.comfort)
        )

# Use an infinitesimaly small number as tie-breaker in case other values are equal
WeightsExp.sortByTime        = WeightsExp(1, EPSILON, EPSILON)
WeightsExp.sortByCost        = WeightsExp(EPSILON, 1, EPSILON)
WeightsExp.prioritizeTime    = WeightsExp(1, .5, .35)
WeightsExp.prioritizeCost    = WeightsExp(.65, 1, .2)
WeightsExp.prioritizeComfort = WeightsExp(.5, .35, 4)


class PathInfo:
    def __init__(self, total, node, prevPathInfo, fromEdge, nodeSet=None):
        self.total = total
        self.node = node
        self.prev = prevPathInfo
        self.edge = fromEdge
        self.nodeSet = nodeSet if nodeSet else { node }

    @classmethod
    def NewFrom(cls, prevPathInfo, fromEdge, weights, useBitmask=False, nodeDict=None):
        total = prevPathInfo.total + weights.Eval(fromEdge)
        node = fromEdge.to
        # Whe initializing from existing PathInfo, we
        # copy its edgeSet and add the new edge we came from
        nodeSet = None
        if useBitmask and nodeDict:
            nodeSet = prevPathInfo.nodeSet | (1 << nodeDict[node])
        elif not useBitmask:
            nodeSet = prevPathInfo.nodeSet.copy()
            nodeSet.add(node)
        else: nodeSet = { node }

        return cls(total, node, prevPathInfo, fromEdge, nodeSet)

    def __lt__(self, other):
        return self.total < other.total
    def __gt__(self, other):
        return self.total > other.total

import heapq
import bisect

def Search(adjList: AdjList, weights, source, dest, numRanks: int):
    heap = []

    nodeDict = {node: idx for idx, node in enumerate(adjList.nodes)}

    heapq.heappush(heap, PathInfo(0, source, None, None, 1 << nodeDict[source]))
    shortestRoute = {node: [] for node in adjList.nodes}


    while heap:
        current = heapq.heappop(heap)
        dist, node, prev = current.total, current.node, current.prev

        # Pruning: do not search known long paths
        if len(shortestRoute[node]) >= numRanks and dist > shortestRoute[node][-1][0]:
            continue

        # Record current path, discarding longer ones
        bisect.insort(shortestRoute[node], (dist, current), key=lambda x: x[0])
        if len(shortestRoute[node]) > numRanks:
            shortestRoute[node].pop()

        for edge in adjList.graph.get(node, []):
            nextNode = edge.to

            # Avoid multiple accesses on the same node (simple paths only)
            if current.nodeSet & (1 << nodeDict[nextNode]):
                continue

            heapq.heappush(heap, PathInfo.NewFrom(current, edge, weights, True, nodeDict))

    shortestRoute = shortestRoute[dest]
    routeRes = [(routeHead[0], []) for routeHead in shortestRoute]
    for routeRank in range(len(shortestRoute)):
        pathHead = shortestRoute[routeRank][1]
        while pathHead and pathHead.edge:
            routeRes[routeRank][1].append(pathHead.edge)
            pathHead = pathHead.prev
        # reverse to get source => dest order
        routeRes[routeRank][1].reverse()
    
    return routeRes


def ToSafeReal(s, default: float = 0, positiveOnly = False):
    try:
        ret = float(s)
        return default if (ret < 0 and positiveOnly) else ret
    except (ValueError, TypeError): return default

def GetSafeElement(idx, fromList, default=None):
    try: return fromList[idx]
    except (KeyError, IndexError): return default

__all__ = ["Weights", "WeightsExp", "Edge", "AdjList",
           "EPSILON", "Search", "ToSafeReal", "GetSafeElement"]

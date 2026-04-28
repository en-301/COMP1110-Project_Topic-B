from Modules.Core import *
from Modules.PathManager import *

path = "./Data/"

def DFSTopPaths(graph: AdjList, weights: Weights, source, dest, numRanks: int):
    paths = []

    def DFS(node, path, weight, visited):
        if node == dest:
            paths.append((weight, path[:]))
            return

        visited.add(node)
        for edge in graph.graph.get(node, []):
            if edge.to not in visited:
                edgeWeight = weights.Eval(edge)
                DFS(edge.to, path + [edge], weight + edgeWeight, visited)
        visited.remove(node)

    DFS(source, [], 0.0, set())

    # Sort by total cost ascending
    paths.sort(key=lambda x: x[0])

    # Return top-k
    return paths[:numRanks]

if __name__ == "__main__":
    # --- graph reading ---
    # Features used: PathManager.ReadFile(), PathManager.ReadGraph()
    fileName=ReadFile(path)
    if fileName == None:
        exit()
    print()
    graph = ReadGraph(fileName=fileName)
    if graph == None:
        exit()

    nodes = [node for node in sorted(list(graph.nodes))]
    testTot = 0
    testErr = 0

    print(f"=== Enumerating {len(nodes)} location{"s" if len(nodes) > 1 else ""} ===")
    for node in nodes: print(node)

    print("""
=== Presets ===
1. Prioritize time
2. Prioritize time (aggresive)
3. Prioritize cost
4. Prioritize cost (aggresive)
5. Prioritize comfort
6. Custom
    """)

    from GraphManager import InputNumber
    
    weightChoice = InputNumber("Select preset (1-6): ", 1, 6, True)

    # weightChoice is currently a number - convert it to a specific Weights object
    if weightChoice == 6:   # custom weights
        weightChoice = WeightsExp(
            max(1e-4, InputNumber("Input custom weight (0-10) for time: ",    0, 10) / 10),
            max(1e-4, InputNumber("Input custom weight (0-10) for cost: ",    0, 10) / 10),
            max(1e-4, InputNumber("Input custom weight (0-10) for comfort: ", 0, 10) / 10),
        )
    else:   # preset weights
        weightChoice = [
            WeightsExp.prioritizeTime,
            WeightsExp.sortByTime,
            WeightsExp.prioritizeCost,
            WeightsExp.sortByCost,
            WeightsExp.prioritizeComfort
        ][weightChoice - 1]

    numRanks = ""
    while not numRanks.isdigit():
        numRanks = input("Input the number of top recommendations to compare with: ").strip()
        if not numRanks.isdigit():
            print(f"Error: {numRanks} is not an integer")
    numRanks = int(numRanks)
    print()

    for source in nodes:
        for dest in nodes:
            if source == dest: continue

            paths = Search(graph, weightChoice, source, dest, numRanks)
            pathsVerified = DFSTopPaths(graph, weightChoice, source, dest, numRanks)
        
            if len(paths) != len(pathsVerified):
                print(f"Case {source}->{dest}: Solution size mismatch,", end=" ")
                print(f"read {len(paths)}, expected {len(pathsVerified)}")
                testErr += 1
            else:
                n = len(paths)
                bHasErr = False
                for i in range(n):
                    if abs(paths[i][0] - pathsVerified[i][0]) > EPSILON:
                        print(f"Case {source}->{dest}, choice #{i+1}:", end=" ")
                        print(f"aggregate weight mismtach,", end=" ")
                        print(f"read {paths[i][0]:.4f}, expected {pathsVerified[i][0]:.4f}")
                        bHasErr = True
                        break
                if bHasErr: testErr += 1
            testTot += 1

    print(f"\n=== Test result: {testTot - testErr}/{testTot}", end=" ")
    print(f"({((testTot - testErr) * 100.0 / testTot):.4f})% ===")

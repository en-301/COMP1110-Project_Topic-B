from Modules.Core import *
from Modules.PathManager import *

def InputNumber(prompt: str, lb = 0, ub = 1, integerOnly: bool = False):
    ret = None
    while True:
        ret = ""
        # Prompt the user to input until a non-empty line is retrieved
        while len(ret) == 0: ret = input(prompt).strip()

        try:    # if the input is a number
            ret = float(ret)
            if ret < lb or ret > ub:    # if input is out of range
                print(f"Error: value must be from {lb} to {ub}") 
            # if input is a float but only integers are allowed
            elif abs(ret - round(ret)) > 1e-4 and integerOnly:
                print(f"Error: value must be an integer")
            else: # if input is valid, exit the loop
                return (int(round(ret)) if integerOnly else ret)
        except ValueError:  # if the input is not a number
            print(f"Error: \"{ret}\" is not a number")


if __name__ == "__main__":
    # --- graph reading ---
    # Features used: PathManager.ReadFile(), PathManager.ReadGraph()
    fileName=ReadFile()
    if fileName == None:
        input("\nPress enter to exit...")
        exit()
    print()
    graph = ReadGraph(fileName=fileName)
    if graph == None:
        input("\nPress enter to exit...")
        exit()

    bIsInMainLoop = True
    while bIsInMainLoop:
        print(f"=== Found {graph.n} location{"s" if graph.n > 1 else ""} ===")
        for node in sorted(list(graph.nodes)): print(node)
        print()

        # --- source/dest reading ---
        # Keep reading source/destination until valid
        bIsInInput = True

        while bIsInInput:
            sourceNode = None
            bIsInSourceInput = True
            while bIsInSourceInput:
                sourceNode = input("Input starting location: ").strip()

                # For invalid source: keep bIsInSourceInput as True and loop again
                if sourceNode not in graph.nodes:
                    print("Location not found. Check the spelling and enter again.")       
                else: # For valid source: exit from source input loop and proceed
                    bIsInSourceInput = False
    
            destNode = None
            bIsInDestInput = True
            while bIsInDestInput:
                destNode = input(
                    "Input destination (empty line: return to starting location): ").strip()

                # For empty line: stop inputting destination by breaking the local loop,
                # but do not reset bIsInInput (next loop prompts source from the start)
                if destNode == "":
                    print()
                    bIsInDestInput = False

                # For invalid destination: stay in destination input loop
                elif destNode not in graph.nodes:   
                    print("Location not found. Check the spelling and enter again.")

                # For overlaps with source: stay in destination input loop
                elif destNode == sourceNode:
                    print("Overlapping source and destination. Please enter a different location.")

                else:   # for valid inputs: exit both the destination and main input loops
                    bIsInDestInput = False
                    bIsInInput = False

        # --- path finding ---
        # Find top 3 shortest paths from node 0 to node 3 with weighting file
        # Features used: Core.Search, Core.Weight

        print("""
=== Presets ===
1. Prioritize time
2. Prioritize time (aggresive)
3. Prioritize cost
4. Prioritize cost (aggresive)
5. Prioritize comfort
6. Custom
        """)
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

        paths = Search(graph,
                       weightChoice,
                       source=sourceNode, dest=destNode, numRanks=5)

        idx: int = 0
        print(f"\n=== Top {len(paths)} recommendations ===\n")
        for total, edges in paths:
            idx += 1
            print(f"-- Route {idx:^3} --")
            print(f"Total travel time: {sum(edge.time for edge in edges):.0f} minutes")
            print(f"Total cost: {sum(edge.cost for edge in edges):.2f} HKD")
            print(f"Average comfort: {(sum(edge.comfort for edge in edges) / len(edges)):.2f}")
            # reconstruct nodes from edges
            nodes = [edges[0].source] + [e.to for e in edges]
            print("Path: ")
            for edge in edges:
                print(f"[{GetSafeElement("mode", edge.customData, "walking")}] ", end="")
                print(f"{edge.source} -> {edge.to}")
            print()

        continueCmd = ""
        while len(continueCmd) < 1 or (continueCmd != 'y' and continueCmd != 'n'):
            continueCmd = input("Continue? (y/n): ").strip().lower()
            if len(continueCmd) > 1: continueCmd = continueCmd[0] 
        bIsInMainLoop = (continueCmd[0] == 'y')
        print()

from Modules.Core import *

def ReadFile(path="./Data/"):
    from pathlib import Path

    # Search recursively for all .csv files
    folderPath = Path(path)
    files = list(folderPath.rglob("*.csv"))
    numFiles = len(files)

    if numFiles < 1:
        print("No map configs detected.")
        print(f"To use a config (.csv format), move it into {path} directory.")
        return None

    print(f"=== {numFiles} graph{"s" if numFiles > 1 else ""} detected ===")
    idx = 1
    for file in files:
        print(f"{idx}: {file.name}")
        idx += 1
    print()

    fileName = "<empty file>"
    cmd = "<error cmd>"
    while (len(cmd) < 1) or (cmd != 'y'):
        idx = int(ToSafeReal(
            input(f"Enter index of graph to use (from 1 to {len(files)}): "), 1
        ))
        if idx < 1: idx = 1
        elif idx > len(files): idx = len(files)
        idx -= 1
        
        cmd = "<error cmd>" # read until cmd is either 'y' or 'n'
        fileName = files[idx].name
        while (len(cmd) < 1) or (cmd != 'y' and cmd != 'n'):
            cmd = input(f"Confirm config {fileName} (y/n): ").strip().lower()
            if len(cmd) > 0: cmd = cmd[0]
        # if cmd == "y": exit the loop
        # if no: prompt the user to enter again
        
    return fileName

def ReadGraph(pathDir = "./Data/", fileName : str = "example.csv"):
    from os import path
    fileDir = path.join(pathDir, fileName)
    
    try:
        with open(fileDir, newline="") as file:
            isDirected = (file.readline().strip().upper() == "DIRECTED")

            import csv
            reader = csv.reader(file)       

            retGraph = AdjList(0)
            for row in reader:
                if len(row) >= 3:
                    source, to = row[0], row[1]
                    time    = ToSafeReal(GetSafeElement(2, row), positiveOnly=True)
                    cost    = ToSafeReal(GetSafeElement(3, row), positiveOnly=True)
                    comfort = ToSafeReal(GetSafeElement(4, row))
                    mode = GetSafeElement(5, row, "<unknown mode>")
                    edge = Edge(source, to, time, cost, comfort, customInfo={"mode": mode})

                    if isDirected: retGraph.AddEdge(edge)
                    else: retGraph.AddEdgeBidirectional(edge)
            return retGraph

    except FileNotFoundError:
        print(f"Error: map config \"{fileName}\" cannot be found.")
        print(f"to load the file, move it into {pathDir} directory.")
        return None

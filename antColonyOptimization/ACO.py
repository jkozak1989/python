import numpy as np
from numpy.random import choice as np_choice

"""
N = 10
a = np.random.random_integers(1,20,size=(N,N))
aSymm = np.tril(a) + np.tril(a, -1).T
for i in range(N):
    aSymm[i][i] = 0
"""

distanceMatrix = np.array([
    [ 0, 16,  5, 14, 16,  6, 10, 13,  8, 14],
    [16,  0, 18, 11,  5,  5, 19, 16, 14, 16],
    [ 5, 18,  0,  4, 20, 18, 12, 14,  4, 10],
    [14, 11,  4,  0,  3, 18,  8, 19, 16, 18],
    [16,  5, 20,  3,  0,  8,  2,  6, 14,  9],
    [ 6,  5, 18, 18,  8,  0,  4, 11,  5,  7],
    [10, 19, 12,  8,  2,  4,  0, 16,  4, 18],
    [13, 16, 14, 19,  6, 11, 16,  0, 13, 12],
    [ 8, 14,  4, 16, 14,  5,  4, 13,  0,  7],
    [14, 16, 10, 18,  9,  7, 18, 12,  7,  0]])
pheromoneMatrix = np.ones(distanceMatrix.shape)
numberOfAnts = 50
numberOfIterations = 50
decay = 0.95
pheromoneWeight = 1
distanceWeight = 1
shortestPath = []
shortestDistance = 9999
allTimeShortestPath = []

def generate_all_paths():
    allPaths = []
    for i in range(numberOfAnts):
        path = generate_path(0)
        allPaths.append([path, generate_path_distance(path)])
    return allPaths

def generate_path(start):
    path = []
    visited = set()
    visited.add(start)
    prev = start
    for i in range(len(distanceMatrix) - 1):
        move = pick_way(pheromoneMatrix[prev], distanceMatrix[prev], visited)
        path.append((prev, move))
        prev = move
        visited.add(move)
    path.append((prev, start)) 
    return path

def pick_way(pheromone, dist, visited):
    pheromone = np.copy(pheromone)
    pheromone[list(visited)] = 0
    row = pheromone ** pheromoneWeight * ((np.divide(np.ones(dist.shape), dist, out=np.zeros_like(np.ones(dist.shape)), where=dist!=0)) ** distanceWeight)

    normRow = row / row.sum()
    move = np_choice(range(len(distanceMatrix)), 1, p=normRow)[0]
    return move

def generate_path_distance(path):
    totalDistance = 0
    for i in path:
        totalDistance += distanceMatrix[i]
    return totalDistance

def spread_pheronome(allPaths, nAnts):
    sortedPaths = sorted(allPaths, key=lambda x: x[1])
    for path, dist in sortedPaths[:nAnts]:
        for move in path:
            pheromoneMatrix[move] += 1.0 / distanceMatrix[move]

for i in range(numberOfIterations):
    allPaths = generate_all_paths()
    if i == 0:
        shortestPath = allPaths[0]
        allTimeShortestPath = allPaths[0]
    spread_pheronome(allPaths, numberOfAnts)
    shortestPath = min(allPaths, key=lambda x: x[1])
    if shortestPath[1] < allTimeShortestPath[1]:
        allTimeShortestPath = shortestPath            
    pheromoneWeight = pheromoneWeight * decay     
    if i % 10 == 0 and i != 0:
        print(f"{i} iterations done.")
print(f"Shortest path is {allTimeShortestPath[0]}, shortest distance is {allTimeShortestPath[1]}.")

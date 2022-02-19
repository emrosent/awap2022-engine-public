import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

import numpy as np

#THRESHOLD is the minimum size of a population value that you want to include
def any_cluster_helper(map, seen, current, i, j, THRESHOLD=0):
    seen[i][j] = True
    tile = map[i][j]
    sum = 0
    if tile.structure == None:
        if tile.population > THRESHOLD:
            current[i][j] = tile.population
            sum += tile.population
            if (i > 0 and not seen[i-1][j]):
                sum += any_cluster_helper(map, seen, current, i-1, j)
            if (i < len(map)-1 and not seen[i+1][j]):
                sum += any_cluster_helper(map, seen, current, i+1, j)
            if (j > 0 and not seen[i][j-1]):
                sum += any_cluster_helper(map, seen, current, i, j-1)
            if (j < len(map[0])-1 and not seen[i][j+1]):
                sum += any_cluster_helper(map, seen, current, i, j+1)
    return sum

#helper function to identify clusters of population
#MINSIZE is the minimum size of the cluster you want
def get_any_cluster(map, MINSIZE=0):
    clusters = dict()
    for i in range(len(map)):
        for j in range(len(map[0])):
            current = np.full((len(map), len(map[0])), 0)
            seen = np.full((len(map), len(map[0])), None)
            result = any_cluster_helper(map, seen, current, i, j)
            if result > MINSIZE:
                x_values, y_values, num = 0,0,0
                for i in range(len(current)):
                    for j in range(len(current[i])):
                        if current[i][j] != 0:
                            x_values += i
                            y_values += j
                            num += 1
                clusters[result] = (float(x_values)/float(num), float(y_values)/float(num))
    return clusters
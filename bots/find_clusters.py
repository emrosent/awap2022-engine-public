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
    height, width = len(map), len(map[0])
    for i in range(height):
        for j in range(width):
            current = np.full((height, width), 0)
            seen = np.full((height, width), None)
            result = any_cluster_helper(map, seen, current, i, j)
            if result > MINSIZE:
                x_values, y_values, num = 0,0,0
                for i in range(height):
                    for j in range(width):
                        if current[i][j] != 0:
                            x_values += i
                            y_values += j
                            num += 1
                clusters[(float(x_values)/float(num), float(y_values)/float(num))] = result
    return clusters

#returns True if we see other bot's structures in the radius (of the square), false o/w
def check_radius(map, team, center, CHECK_RADIUS):
    for i in range(min(0, center[0]-CHECK_RADIUS), max(center[0]+CHECK_RADIUS, len(map))):
        for j in range(min(0, center[1]-CHECK_RADIUS), max(center[1]+CHECK_RADIUS, len(map[0])):
            if map[i][j].team == (1-team): #TEAM = 0 or 1, so this is the opposite team (as opposed to neutral which is 2)
                return True
    return False

#Parameters: map, the team you are on, the current clusters dictionary, and the radius you want to check
#(ok, it's a square, not technically a circle.)
#Does not return anything, but changes clusters and removes the ones that are no longer relevant.
def update_clusters(map, team, clusters, CHECK_RADIUS=2):
    for cluster in clusters.keys():
        if check_radius(map, team, cluster, CHECK_RADIUS):
            clusters.pop(cluster) #removes the cluster

#def try_towers(map, cluster):

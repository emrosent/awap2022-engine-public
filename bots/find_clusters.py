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
        for j in range(min(0, center[1]-CHECK_RADIUS), max(center[1]+CHECK_RADIUS, len(map[0]))):
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

def yoink(x, y, map):
  if x >= 0 and x < len(map) and y >= 0 and y < len(map[0]):
    return map[x][y].population
  return 0

def get_potential(x, y, map):
  potential = 0
  m = [-1, 0, 1]
  for i in m:
    for j in m:
      potential += yoink(x + i, y + j, map)
  potential += yoink(x + 2, y, map)
  potential += yoink(x - 2, y, map)
  potential += yoink(x, y + 2, map)
  potential += yoink(x, y - 2, map)
  return potential

def all_potentials(map):
  potentials = [[0] * len(map[0])] * len(map)
  for x in range(len(map)):
    for y in range(len(map[0])):
      potentials[x][y] = get_potential(x, y, map)
  return potentials

def potential_coords_max(pot1, pot2):
    if (pot1[0] > pot2[0]):
        return pot1
    else:
        return pot2

#returns coordinate in the cluster with the highest potential
#seen : an array the same size as map that should be filled with None at first
def try_towers_helper(map, seen, i, j, THRESHOLD=0):
    seen[i][j] = True
    tile = map[i][j]
    potential = (0, (i,j))
    if tile.structure == None and tile.population > THRESHOLD:
        potential = (get_potential(i, j, map), (i,j))
        if (i > 0 and not seen[i-1][j]):
            potential = potential_coords_max(potential, (any_cluster_helper(map, seen, i-1, j), (i-1, j)))
        if (i < len(map)-1 and not seen[i+1][j]):
            potential = potential_coords_max(potential, (any_cluster_helper(map, seen, i+1, j), (i+1, j)))
        if (j > 0 and not seen[i][j-1]):
            potential = potential_coords_max(potential, (any_cluster_helper(map, seen, i, j-1), (i, j-1)))
        if (j < len(map[0])-1 and not seen[i][j+1]):
            potential = potential_coords_max(potential, (any_cluster_helper(map, seen, i, j+1), (i, j+1)))
    return potential

def get_clusters_range(map, clusters, min_x, max_x, min_y, max_y, MINSIZE = 0):
    height, width = len(map), len(map[0])
    for i in range(min_x, max_x):
        for j in range(min_y, max_y):
            current = np.full((height, width), 0)
            seen = np.full((height, width), False)
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

#input: map, cluster = (i,j)
#outputs: (x, y) coordinates of the tower that you should build
#also updates clusters dictionary.
def try_towers(map, clusters, cluster, THRESHOLD = 0):
    height, width = len(map), len(map[0])
    seen = np.full((height, width), None)
    (i, j) = cluster
    potential = try_towers_helper(map, seen, i, j, THRESHOLD)
    x_values, y_values = set(), set()
    for i in range(height):
        for j in range(width):
            x_values.add(i)
            y_values.add(j)
    get_clusters_range(map, clusters, min(x_values), max(x_values)+1, min(y_values), max(y_values)+1)
    return potential[1]
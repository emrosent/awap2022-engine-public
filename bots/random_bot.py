import sys

import random
from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

'''
This bot randomly builds one building per turn (on a valid tile).
Note that your bot may build multiple structures per turn, as long as you can afford them.
'''

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

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0

        return


    def play_turn(self, turn_num, map, player_info):
        # if (turn_num == 0):
        #     self.clusters = get_any_cluster(map)
        # v=list(self.clusters.values())
        # k=list(self.clusters.keys())
        # cluster = k[v.index(max(v))]
        # cluster = (int(cluster[0]), int(cluster[1]))
        # print(try_towers(map, self.clusters, cluster))

        self.MAP_WIDTH = len(map)
        self.MAP_HEIGHT = len(map[0])

        # find tiles on my team
        my_structs = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        my_structs.append(st)

        # call helper method to build randomly
        self.try_random_build(map, my_structs, player_info)

        # randomly bid 1 or 2
        self.set_bid(random.randint(1, 2))

        return


    ''' Helper method for trying to build a random structure'''
    def try_random_build(self, map, my_structs, player_info):
        # choose a type of structure to build
        # build a tower for every 4 roads
        if len(my_structs) % 5 == 4:
            build_type = StructureType.TOWER
        else:
            build_type = StructureType.ROAD

        # identify the set of tiles that we can build on
        valid_tiles = []

        # look for a empty tile that is adjacent to one of our structs
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                # check this tile contains one of our structures
                st = map[x][y].structure
                if st is None or st.team != player_info.team:
                    continue
                # check if any of the adjacent tiles are open
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    (nx, ny) = (st.x + dx, st.y + dy)
                    # check if adjacent tile is valid (on the map and empty)
                    if 0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT:
                        if map[nx][ny].structure is None:
                            cost = build_type.get_base_cost() * map[nx][ny].passability
                            # check if my team can afford this structure
                            if player_info.money >= cost:
                                # attempt to build
                                valid_tiles.append((nx, ny))

        # choose a random tile to build on
        if(len(valid_tiles) > 0):
            tx, ty = random.choice(valid_tiles)
            self.build(build_type, tx, ty)

from math import trunc
import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

from pprint import pprint

import numpy as np


################################################################################
### BEGIN find_clusters.py
################################################################################


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
                clusters[(int(float(x_values)/float(num)), int(float(y_values)/float(num)))] = result
    return clusters

#returns True if we see other bot's structures in the radius (of the square), false o/w
def check_radius(map, team, center, CHECK_RADIUS):
  for i in range(max(0, int(center[0]-CHECK_RADIUS)), min(int(center[0]+CHECK_RADIUS), len(map))):
      for j in range(max(0, int(center[1]-CHECK_RADIUS)), min(int(center[1]+CHECK_RADIUS), len(map[0]))):
          if map[i][j].structure and map[i][j].structure.team != team: #TEAM = 0 or 1, so this is the opposite team (as opposed to neutral which is 2)
              return True
  return False

#Parameters: map, the team you are on, the current clusters dictionary, and the radius you want to check
#(ok, it's a square, not technically a circle.)
#Does not return anything, but changes clusters and removes the ones that are no longer relevant.
def update_clusters(map, team, clusters, CHECK_RADIUS=2):
    clustersToKill = []
    for cluster in clusters.keys():
        if check_radius(map, team, cluster, CHECK_RADIUS):
            clustersToKill.append(cluster) #removes the cluster
    for cluster in clustersToKill:
      clusters.pop(cluster)
    print(clusters.size)

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
            potential = potential_coords_max(potential, (try_towers_helper(map, seen, i-1, j)))
        if (i < len(map)-1 and not seen[i+1][j]):
            potential = potential_coords_max(potential, (try_towers_helper(map, seen, i+1, j)))
        if (j > 0 and not seen[i][j-1]):
            potential = potential_coords_max(potential, (try_towers_helper(map, seen, i, j-1)))
        if (j < len(map[0])-1 and not seen[i][j+1]):
            potential = potential_coords_max(potential, (try_towers_helper(map, seen, i, j+1)))
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
                clusters[int(float(x_values)/float(num)), int(float(y_values)/float(num))] = result

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
            if map[i][j].population > 0:
              x_values.add(i)
              y_values.add(j)
    if clusters[cluster] > 15:
      clusters.pop(cluster)
      get_clusters_range(map, clusters, min(x_values), max(x_values)+1, min(y_values), max(y_values)+1)
    else:
      clusters.pop(cluster)
    return potential[1]

################################################################################
### END find_clusters.py
################################################################################
### BEGIN dijkstra.py
################################################################################


class Dijkstra:

    def findMin(pV,seen):
        res = None
        bestI = 0
        i = 0
        while res == None and i < len(pV):
            if seen[i] == 0:
                res = pV[i]
                bestI = i
            i += 1
        #print(f"woooo: {res}")
        #print(pV)
        while i < len(pV):
            if seen[i] == 0 and pV[i] < res:
                res = pV[i]
                bestI = i
            i += 1
        return bestI,res


    #s = vertex (int)
    #G = (V,E) where V is a list of vertices, E = adj list of (neighbor,cost)
    def dijkstra(self,s,G):
        
            V,E = G

            seen = [0 for v in V]

            modV = []
            for v in V:
                modV.append(sys.maxsize)
            modV[s] = 0 


            prev_nodes = dict()

            n = len(V) - 1
            # print(modV)
            while n > 0:
                curr,val = self.findMin(modV,seen)
                
                #print(f"curr : {curr} val : {val}")
                neighbors = E[curr]

                for neigh,val in neighbors:
                    if modV[curr] + val < modV[neigh]:
                        prev_nodes[neigh] = curr
                        modV[neigh] = modV[curr] + val
                    #modV[neigh] = min(modV[neigh], modV[curr] + val)
                    #print(f"new val for {neigh} : {modV[neigh][0]}")
                    #if seen[neigh] == 0: 
                    #    prev_nodes[neigh] = curr
                
                seen[curr] = 1
                
                n -= 1

            #print(modV)
            # print(prev_nodes)
            return prev_nodes,modV

################################################################################
### END dijkstra.py
################################################################################

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0
        self.roads = set()
        self.towers = set()
        self.currPath = []
        self.clusters = dict()
        self.target_tower = None
        return

    
    def set_dijkstra(self, map):
      def get_weight(x, y):
        st = map[x][y].structure
        return 0 if st and st.team == self.team else map[x][y].passability
      V = []
      E = []
      for y in range(self.MAP_HEIGHT):
        for x in range(self.MAP_WIDTH):
          edges = []
          V.append(x + (y * self.MAP_WIDTH))
          if (x != 0):
            # go left
            edges.append((x - 1 + (y * self.MAP_WIDTH), get_weight(x-1, y)))
          if (x + 1 != self.MAP_WIDTH):
            # go right
            edges.append((x + 1 + (y * self.MAP_WIDTH), get_weight(x+1, y)))
          if (y != 0):
            # go up?
            edges.append((x + ((y - 1) * self.MAP_WIDTH ), get_weight(x, y-1)))
          if (y + 1 != self.MAP_HEIGHT):
            # go down?
            edges.append((x + ((y + 1) * self.MAP_WIDTH), get_weight(x, y+1)))
          E.append(edges)
      
      (prev_nodes, modV) = Dijkstra.dijkstra(Dijkstra, self.generators[0], (V, E))
      self.prev_nodes = prev_nodes
      self.modV = modV


    def best_cluster(self, map, clusters):
      # step 2. use heuristic to find the most valuable cluster
      bestCluster, bestValue = None, None
      for cluster in clusters:
        x, y = cluster[0], cluster[1]
        population = clusters[cluster]
        distance = self.modV[x + (y * self.MAP_WIDTH)]
        if distance != 0:
          totalValue = population / distance
        else:
          totalValue = 0
        if bestCluster == None or totalValue > bestValue:
          bestCluster = (x, y)
          bestValue = totalValue
      return bestCluster

    
    # sets self.currPath to be a list of remaining paths to build!
    def set_path(self, x, y):
      src = self.generators[0]
      path = []
      node = x + y * self.MAP_WIDTH
      while node != src:
        prev_node = self.prev_nodes[node]
        path.append(prev_node)
        node = prev_node
      path.pop()
      path.reverse()
      self.currPath = path
    
    def set_target_tower(self, map):
      # need to calculate dijkstra's here
      self.set_dijkstra(map)

      # step 2. use heuristic to find the most valuable cluster
      self.bestCluster = self.best_cluster(map, self.clusters)
      
      # step 3. use try_towers to find the tower placement for that cluster
      tower = try_towers(map, self.clusters, self.bestCluster)
      self.target_tower = tower

    def play_turn(self, turn_num, map, player_info):
        self.MAP_WIDTH = len(map)
        self.MAP_HEIGHT = len(map[0])

        if turn_num == 0:
          self.team = player_info.team
          generators = []
          for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
              structure = map[x][y].structure
              if structure and structure.team == player_info.team and structure.type == StructureType.GENERATOR:
                  generators.append(x + (y * self.MAP_WIDTH))
          self.generators = generators
          self.clusters = get_any_cluster(map)
          self.set_dijkstra(map)

        
        # update_clusters(map, self.team, self.clusters)

        if self.target_tower == None:
          self.set_target_tower(map)
          self.set_path(self.target_tower[0], self.target_tower[1])

        pprint(self.currPath)
        pprint(self.target_tower)

        money = player_info.money
        doWeReverse = False
        while True:
          if len(self.currPath) != 0:
            tileToBuy = self.currPath[0]
            x, y = tileToBuy % self.MAP_WIDTH, tileToBuy // self.MAP_WIDTH
            if doWeReverse:
              x, y = y,x
            doWeReverse = not doWeReverse
            cost = StructureType.ROAD.get_base_cost() * map[x][y].passability
            # print(f"attempting to build road at: {x}, {y}")
            # print(f"current money: {money}")
            if money < cost:
              # print("out of money, stopping for now\n")
              break
            money -= cost
            # print("buying!\n")
            self.build(StructureType.ROAD, x, y)
            self.roads.add(tileToBuy)
            self.currPath = self.currPath[1:]
          else:
            x, y = self.target_tower
            cost = StructureType.ROAD.get_base_cost() * map[x][y].passability
            if money < cost:
              break
            self.build(StructureType.TOWER, x, y)
            self.towers.add(self.target_tower)
            # self.clusters.pop(self.best_cluster)
            money -= cost
            self.set_target_tower(map)
            self.set_path(self.target_tower[0], self.target_tower[1])
    


        # pprint(self.heuristicArray)
        '''
        1. find clusters
        2. find distance + paths to all cluster points
        3. use heuristic to find the most valuable cluster
        4. use try_towers to find the tower placement for that cluster
        5. build roads to that location and then build a tower there
        '''

        return

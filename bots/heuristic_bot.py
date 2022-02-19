import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

from pprint import pprint

import numpy as np

def yoink(x, y, map):
  if x >= 0 and x < len(map) and y >= 0 and y < len(map[0]):
    return map[x][y].population
  return 0

def inRange(point,width,height):
  x,y = point
  return 0 <= x and x < width and 0 <= y and y < height

#checks if a point is adjacent to any structure owned
def isAdj(x,y,map,player_info):
  checks = [(x,y+1),(x,y-1),(x-1,y),(x+1,y)]

  for (cX,cY) in checks:
    if inRange((cX,cY),len(map),len(map[0])) and map[cX][cY].structure != None and map[cX][cY].structure.team == player_info.team:
      return True 

  return False



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


class Dijkstra:

    def findMin(pV,seen):
        res = None
        i = 0
        while res == None and i < len(pV):
            if seen[i] == 0:
                res = pV[i]
            i += 1
        while i < len(pV):
            if seen[i] == 0 and pV[i][0] < res[0]:
                res = pV[i]
            i += 1
        return res


    #s = vertex (int)
    #G = (V,E) where V is a list of vertices, E = adj list of (neighbor,cost)
    def dijkstra(self,s,G):
        
            V,E = G

            seen = [0 for v in V]

            modV = []
            for v in V:
                modV.append((1000,v))
            modV[s] = (0,s)


            prev_nodes = dict()

            n = len(V) - 1

            while n > 0:
                val,curr = self.findMin(modV,seen)
                
                #print(f"curr : {curr} val : {val}")
                neighbors = E[curr]

                for neigh,val in neighbors:
                    modV[neigh] = (min(modV[neigh][0], modV[curr][0] + val),neigh)
                    #print(f"new val for {neigh} : {modV[neigh][0]}")
                    if seen[neigh] == 0: prev_nodes[neigh] = curr
                
                seen[curr] = 1
                
                n -= 1


            return prev_nodes,modV


class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0

        return


    def play_turn(self, turn_num, map, player_info):
        # we will have the profit potential of each tile.
        # we will be able to calculate the single-source shortest path
        # to any point from the generator
        # 
        # so we run single-source shortest paths from the generators to find the
        #   shortest paths to each tile.
        # then we make a 2d array A that will essentially just be distance/profit
        self.MAP_WIDTH = len(map)
        self.MAP_HEIGHT = len(map[0])

        population_tiles = []
        generators = []
        V = []
        E = []
        for x in range(self.MAP_WIDTH):
          for y in range(self.MAP_HEIGHT):
            edges = []
            V.append(x + (y * self.MAP_HEIGHT))
            if (x != 0):
              # go left
              edges.append((x - 1 + (y * self.MAP_HEIGHT), map[x-1][y].passability))
            if (x + 1 != self.MAP_WIDTH):
              # go right
              edges.append((x + 1 + (y * self.MAP_HEIGHT), map[x+1][y].passability))
            if (y != 0):
              # go up?
              edges.append((x + ((y - 1) * self.MAP_HEIGHT ), map[x][y-1].passability))
            if (y + 1 != self.MAP_HEIGHT):
              # go down?
              edges.append((x + ((y + 1) * self.MAP_HEIGHT), map[x][y+1].passability))
            E.append(edges)

        for x in range(self.MAP_WIDTH):
          for y in range(self.MAP_HEIGHT):
            structure = map[x][y].structure
            if structure == None:
              population_tiles.append(((x, y), map[x][y].population))
            elif structure.team == player_info.team and structure.type == StructureType.GENERATOR:
                generators.append(x + (y * self.MAP_HEIGHT))

        (prev_nodes, modV) = Dijkstra.dijkstra(Dijkstra, generators[0], (V, E))
        heuristicArray = []

        # find the shortest path to each nonzero profit square from any generator
        for x in range(self.MAP_WIDTH):
          row = []
          for y in range(self.MAP_HEIGHT):
            profit = get_potential(x, y, map)
            distance = modV[x + (y * self.MAP_HEIGHT)]
            row.append(distance[0] / profit if profit != 0 else 0)
          heuristicArray.append(row)

        pprint(heuristicArray)
        return

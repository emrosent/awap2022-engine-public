import sys
import random
from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC
import numpy as np

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
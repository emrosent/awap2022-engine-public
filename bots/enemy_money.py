
def snoop(self, map):
  self.enemy_money += self.enemy_income
  for x in len(map):
    for y in len(map[0]):
      tile = map[x][y]
      old_tile = self.old_map[x][y]
      ## If a structure for the other team exists and is new
      if tile.structure != None and tile.structure.team != self.team and old_tile.structure == None:
        ## Subtract cost
        self.enemy_money -= tile.structure.get_cost(tile.passability)
        ## If cell tower, increase enemy income
        if tile.structure.get_id == 1:
          self.enemy_income += get_potential(x, y, map)
  ## Store the map for use next turn
  self.old_map = map
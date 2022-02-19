

import sys


V = [0,1,2,3,4]
E = [[(1,2),(2,2)],[(0,2),(2,1),(4,1)],[(0,2),(1,1)],[(4,1)],[(1,1),(3,1)]]

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
            print(modV)
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
            print(prev_nodes)
            return prev_nodes,modV

D = Dijkstra
print(D.dijkstra(D,0,(V,E)))
#print(D.dijkstra(D,1,(V,E)))
#print(D.dijkstra(D,2,(V,E)))
#print(D.dijkstra(D,3,(V,E)))
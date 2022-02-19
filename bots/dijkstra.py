




V = [0,1,2,3,4]
E = [[(1,2),(2,2)],[(0,2),(4,1)],[(0,2)],[(4,1)],[(1,1),(3,1)]]

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

D = Dijkstra
print(D.dijkstra(D,0,(V,E)))
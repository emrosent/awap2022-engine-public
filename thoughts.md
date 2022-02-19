# Thoughts

- Building cell towers early is generally not worth it
- If we're able to cut them off from 51% of the map then we can win
- Better to stockpile money and build on one turn, rather than building incrementally

## General Strategies
- Find clusters of population (i.e. reduce groups of populations to single data points)
- Weighted BFS/Dijkstra's/some other way of finding the cheapest path to each of the clusters
- Calculate the potential of each cluster (in terms of utility and profit but mostly utility)
- Use some combination of cost/potential to decide which cluster to build to first
  - Something to consider - if we can manage to cut the opponent off, this would work really well
- In general, we'll save our money and wait until we can make a "play"
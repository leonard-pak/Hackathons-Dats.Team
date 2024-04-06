
from dataclasses import dataclass
import typing as tp
from collections import deque
from heapq import heappush, heapify, heappop

@dataclass
class Link:
    src: str
    dest: str
    fuel: int


class Universe:
    def __init__(self, links: tp.List[Link], fee = 10, startPlanet = 'Earth', recycler = 'Eden') -> None:
        self.FEE = fee
        self.HOME = startPlanet
        self.RECUCLER = recycler
        self.map: tp.Dict[tp.Dict[int]] = {link.src: {} for link in links}
        for link in links:
            self.map[link.src][link.dest] = link.fuel

    @classmethod
    def create(cls, record) -> 'Universe':
        links: tp.List[Link] = [Link(l[0], l[1], l[2]) for l in record]
        return cls(links)

    def update_cost(self, src: str, dest: str):
        map[src][dest] += self.FEE

    def get_all_neighbors(self, planet):
        neighbors = [n for n in self.map[planet].keys()]
        return neighbors

    def __find_path(self, planet: str, visited: tp.Dict[str, bool], dest: str) -> tp.List[str]:
        if planet == dest:
            return [planet]
        if visited[planet] :
            return []
        visited[planet] = True

        neighbors = self.get_all_neighbors(planet)
        for n in neighbors:
            if path := self.__find_path(n, visited, dest):
                return [planet] + path

        return []

    def __dijkstra(self, src: str, dest: str):
        path_costs = {planet: -1 for planet in self.map.keys()}
        path_dict = {}
        pq = []
        heappush(pq, (0, src))
        path_costs[src] = 0
        while (len(pq) != 0):
            cost, planet = heappop(pq)
            if path_costs[planet] < cost:
                continue
            neigs = self.get_all_neighbors(planet)
            for n in neigs:
                if (path_costs[n] == -1):
                    path_costs[n] = path_costs[planet] + self.map[planet][n]
                    path_dict[n] = planet
                    heappush(pq, (path_costs[n], n))
                elif self.__relax(planet, n, path_costs, path_dict):
                    heappush(pq, (path_costs[n], n))

        path = []
        cur_planet = dest
        while cur_planet != src:
            path.append(cur_planet)
            cur_planet = path_dict[cur_planet]
        path.reverse()
        return path

    def __relax(self, src: str, dest: str, path_costs: tp.Dict[str, int], path: tp.Dict[str, str]):
        if (path_costs[dest] > path_costs[src] + self.map[src][dest]):
            path_costs[dest] = path_costs[src] + self.map[src][dest]
            path[dest] = src
            return True
        return False

    def get_path(self, src: str, dest: str):
        # visited = {planet: False for planet in self.map.keys()}
        # path = self.__find_path(src, visited, dest)
        # path.pop(0) # for dfs

        path = self.__dijkstra(src, dest)

        for i in range(0, len(path) - 1):
            self.update_cost(path[i], path[i + 1])
        self.update_cost(src, path[0])
        return path

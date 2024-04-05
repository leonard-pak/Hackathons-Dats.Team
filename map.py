
from dataclasses import dataclass
import typing as tp

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
        links: tp.List[Link] = [Link(l[0], l[1], l[2]) for l in record['universe']]
        return cls(links)

    def update_cost(self, src: str, dest: str):
        map[src][dest] += self.FEE

    def get_all_neighbors(self, planet):
        neighbors = [n for n in self.map[planet].keys()]
        return neighbors

    def __find_path(self, planet: str, visited: tp.Dict[str, bool], path: tp.List[str], dest: str):
        if visited[planet] :
            return False
        visited[planet] = True

        path.append(planet)
        neighbors = self.get_all_neighbors(planet)
        for n in neighbors:
            if dest == n or self.__find_path(n, visited, path, dest):
                return True
        path.pop()

        return False

    def get_path(self, src: str, dest: str):
        visited = {planet: False for planet in self.map.keys()}
        path = []
        if not self.__find_path(src, visited, path, dest):
            raise RuntimeError(f"no path from {src} to {dest}")
        path.append(dest)
        path.pop(0)
        return path

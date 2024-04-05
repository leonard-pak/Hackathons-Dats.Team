import client
from garbage import GarbageItem, GarbageItemT
from map import Universe
from collections import deque
import typing as tp
from ship import Ship

from time import sleep, time

def solution(client: client.Client):
    res_universe = client.get_universe()
    unvs = Universe.create(res_universe['universe'])
    # ship = Ship.create(res_universe['ship'])

    queue = deque(unvs.get_all_neighbors(unvs.HOME))
    cur_planet = unvs.HOME
    path = []
    cleaned_planets: tp.Set[str] = {unvs.HOME}
    while len(queue) != 0:
        target_planet = queue.popleft()
        if target_planet in cleaned_planets:
            continue

        path.extend(unvs.get_path(cur_planet, target_planet))
        res_travel = client.post_travel(path)
        cur_planet = target_planet
        planetGarbages = GarbageItem.createList(res_travel['planetGarbage'])
        collectGarbage: tp.List[GarbageItem] = [] # TODO

        res_collect = client.post_collect({g.name: g.form for g in collectGarbage})

        if len(res_collect['leaved']) == 0:
            cleaned_planets.add(target_planet)
            queue.extend(unvs.get_all_neighbors(target_planet))
        else:
            queue.appendleft(target_planet)
        path = unvs.get_path(cur_planet, unvs.RECUCLER)

    client.post_travel(path)

if __name__ == '__main__':
    game_client = client.Client()
    solution(game_client)

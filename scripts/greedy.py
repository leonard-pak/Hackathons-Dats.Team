import client
from garbage import GarbageItem
from map import Universe
from collections import deque

from ship import Ship

def solution(client: client.Client):
    res_universe = client.get_universe()
    unvs = Universe.create(res_universe['universe'])
    ship = Ship.create(res_universe['ship'])

    neigs = unvs.get_all_neighbors(unvs.HOME)
    queue = deque(neigs)
    cur_planet = unvs.HOME
    path = []
    while len(queue) != 0:
        target_planet = queue.popleft()

        path.extend(unvs.get_path(cur_planet, target_planet))
        res_travel = client.post_travel(path)
        garbages = GarbageItem.createList(res_travel['planetGarbage'])
        cur_planet = target_planet

        # take garbage
        # if planet not clear, return to queue to begin, else add all neighbors to end

        path = unvs.get_path(cur_planet, unvs.RECUCLER)

    client.post_travel(path)


if __name__ == '__main__':
    game_client = client.Client()
    solution(game_client)

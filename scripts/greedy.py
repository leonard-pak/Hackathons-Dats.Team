import client
from map import Universe
from collections import deque

from ship import Ship

def solution(client: client.Client):
    res_universe = client.get_universe()
    unvs = Universe.create(res_universe)
    ship = Ship.create(res_universe)

    neigs = unvs.get_all_neighbors(unvs.HOME)
    queue = deque(neigs)
    cur_planet = unvs.HOME
    path = []
    while len(queue) != 0:
        planet = queue.popleft()

        path.extend(unvs.get_path(cur_planet, planet))
        client.post_travel(path)
        cur_planet = planet

        # take garbage
        # if planet not clear, return to queue to begin, else add all neighbors to end

        path = unvs.get_path(cur_planet, unvs.RECUCLER)

    client.post_travel(path)


if __name__ == '__main__':
    game_client = client.Client()
    solution(game_client)

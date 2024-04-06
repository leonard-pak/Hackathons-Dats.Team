import client
from garbage import GarbageItem
from map import Universe
from collections import deque
import typing as tp
from ship import Ship
import packing
import time

import logging
import datetime as dt

start_time = dt.datetime.now()
logging.basicConfig(
    filename=f'logs/{start_time.strftime("%H-%M-%S")}.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


# import plotly.express as px

def solution(client: client.Client):
    start = time.time()
    cycle_number = 0

    res_universe = client.get_universe()
    unvs = Universe.create(res_universe['universe'])
    ship = Ship.create(res_universe['ship'])

    cur_planet = res_universe['ship']['planet']['name']
    queue = deque(unvs.get_all_neighbors(cur_planet))
    path = []
    cleaned_planets: tp.Set[str] = {unvs.HOME, cur_planet}
    start_time = time.time()
    while len(queue) != 0:
        cycle_start = time.time()
        cycle_number += 1

        target_planet = queue.popleft()
        if target_planet in cleaned_planets:
            continue

        path = unvs.get_path(cur_planet, target_planet)
        res_travel = client.post_travel(path)
        planetGarbages = GarbageItem.createList(res_travel['planetGarbage'])
        cur_planet = target_planet

        if planetGarbages:
            packager = packing.Packager(ship.storage.capacity_x, ship.storage.capacity_y, planetGarbages)
            collectGarbage = packager.iterate_over_packing(25)
            # break

            res_collect = client.post_collect({g.name: g.form for g in collectGarbage})
        else:
            res_collect = {'leaved': []}

        if len(res_collect['leaved']) == 0:
            cleaned_planets.add(target_planet)
            queue.extend(unvs.get_all_neighbors(target_planet))
        else:
            queue.appendleft(target_planet)

        path = unvs.get_path(cur_planet, unvs.RECUCLER)
        # res_travel = client.post_travel(path)
        cur_planet = unvs.RECUCLER

        cycle_end = time.time()
        msg = f'Cycle {cycle_number} | Cycle time: {cycle_end - cycle_start:.2f}s. | Total elapsed time: {cycle_end - start:.2f}s.'
        print(msg)
        logger.info(msg)

    # client.post_travel(path)

    # packager.occupancy_map[packager.occupancy_map == 0] -= 5
    # fig = px.imshow(packager.occupancy_map, color_continuous_scale='Jet', origin='lower')
    # fig.show()
    print(time.time() - start_time)
    print(len(cleaned_planets) == len(unvs.map))
    logger.info(time.time() - start_time)
    logger.info(len(cleaned_planets) == len(unvs.map))


if __name__ == '__main__':
    game_client = client.Client(period_call=0.3)
    solution(game_client)

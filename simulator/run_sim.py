import json
import typing as tp

import numpy as np

import map_lib
from simulator import simulator_models
import visualize


with open('test_data/world.json') as file:
    records = json.load(file)
    zombie_spots = [simulator_models.ZombieSpot.from_record(record) for record in records['zpots'] if record['type'] == 'default']

for zombie_spot in zombie_spots:
    zombie_spot.x -= 0
    zombie_spot.y -= 0

game_map = np.zeros((150, 150))

game_map[:1] = map_lib.PointType.WALL
game_map[-1:] = map_lib.PointType.WALL
game_map[:, :1] = map_lib.PointType.WALL
game_map[:, -1:] = map_lib.PointType.WALL

for spot in zombie_spots:
    spot.init_possible_directions(game_map)


zombies: tp.List[simulator_models.Zombie] = []

turn_number = 0
for step in range(10):
    turn_number += 1

    for spot in zombie_spots:
        game_map[spot.x, spot.y] = map_lib.PointType.ZOMBIE_SPAWN

    for zombie in zombies:
        zombie_x, zombie_y = zombie.process_round(game_map)
        map_point = game_map[zombie_x][zombie_y]
        if map_point in simulator_models.COLLIDE_OBJECTS:
            zombie.health = 0

    zombies = [zombie for zombie in zombies if zombie.health > 0]

    game_map[np.where(game_map == map_lib.PointType.ZOMBIE)] = map_lib.PointType.EMPTY
    for zombie in zombies:
        game_map[zombie.x, zombie.y] = map_lib.PointType.ZOMBIE

    for zombie_spot in zombie_spots:
        new_zombie = zombie_spot.process_round(turn_number)
        if new_zombie is not None:
            zombies.append(new_zombie)

    if step % 1 == 0:
        visualize.visualize_map(game_map)

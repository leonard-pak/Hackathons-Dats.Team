import random
import typing as tp

import numpy as np

import map_lib
import models
import utils

random.seed(42)


TURN = 75

def get_build(game_map: map_lib.Map) -> tp.List[models.Build]:
    coins = game_map._info.gold
    turn = game_map._info.turn
    build_command_ordered: tp.List[tp.Tuple[int, models.Build]] = []

    main_base = game_map._base.blocks[game_map._base.head_key]
    main_base_pos = main_base.point

    for block in game_map._base.blocks.values():
        block_pos = block.point
        block_x, block_y = int(block_pos[0]), int(block_pos[1])

        new_coords = [
            (block_x + 1, block_y),
            (block_x - 1, block_y),
            (block_x, block_y + 1),
            (block_x, block_y - 1),
        ]

        for new_x, new_y in new_coords:
            if not game_map.is_point_available_to_build(new_x, new_y, turn, turn_break=TURN):
                if abs(int(utils.calc_range(main_base_pos, np.array([new_x, new_y])))) >= 5:
                    continue

            if turn <= TURN:
                neighbours_count = game_map.get_neighbours_count(new_x, new_y)
                build_command_ordered.append(
                (neighbours_count, models.Build(models.Point(new_x, new_y))))
            else:
                distance = abs(int(utils.calc_range(
                    main_base_pos, np.array([new_x, new_y]))))
                build_command_ordered.append(
                    (distance, models.Build(models.Point(new_x, new_y))))

    random.shuffle(build_command_ordered)
    build_command_ordered = sorted(build_command_ordered, key=lambda x: x[0])
    # if turn > TURN:
    #     build_command_ordered = build_command_ordered[:max(coins // 2, 10)]
    return [build_command[1] for build_command in build_command_ordered]

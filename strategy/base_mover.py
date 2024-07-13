import random
import typing as tp

import numpy as np

import map_lib
import models
import utils

random.seed(42)


def get_move_base(game_map: map_lib.Map) -> models.MoveBase:
    main_base = game_map._base.blocks[game_map._base.head_key]
    main_base_pos = main_base.point
    base_pos_x, base_pos_y = int(main_base_pos[0]), int(main_base_pos[1])

    turn = game_map._info.turn
    if turn <= 10000000:
        return models.MoveBase(int(base_pos_x), int(base_pos_y))

    safe_point = game_map.find_save_point3()
    if not safe_point:
        print()
        print('RECIEVED NONE!!!!!!!!')
        print()
        return models.MoveBase(int(base_pos_x), int(base_pos_y))

    x, y = safe_point
    return models.MoveBase(int(x), int(y))

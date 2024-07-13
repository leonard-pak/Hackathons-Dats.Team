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
    base_pos_x, base_pos_y = int()

    return models.MoveBase()
import random
import typing as tp

import map_lib
import models

random.seed(42)


def get_build(game_map: map_lib.Map) -> tp.List[models.Build]:
    build_command: tp.List[models.Build] = []

    for block in game_map._base.blocks.values():
        block_pos = block.point
        block_x, block_y = int(block_pos[0]), int(block_pos[1])

        build_command.append(models.Build(models.Point(block_x + 1, block_y)))
        build_command.append(models.Build(models.Point(block_x - 1, block_y)))
        build_command.append(models.Build(models.Point(block_x, block_y + 1)))
        build_command.append(models.Build(models.Point(block_x, block_y - 1)))

    random.shuffle(build_command)
    return build_command

import typing as tp

import map_lib
import models


def _add_attack_target(attack_targets: tp.Dict, target_pos: tp.Tuple[int, int], target_health: int):
    if target_pos in attack_targets:
        prev_state = attack_targets[target_pos]
        attack_targets[target_pos] = (prev_state[0] + 1, max(prev_state[1], target_health))
    else:
        attack_targets[target_pos] = (1, target_health)


def _attack_targets(game_map: map_lib.Map) -> tp.Dict[tp.Tuple[int, int], tp.Tuple[int, int]]:
    # returns Dict[pos[x, y]: [target_count, max_hp]]
    attack_targets = {}

    for zombie in game_map._zombies.values():
        zombie_pos = zombie.point
        target_pos = (zombie_pos[0], zombie_pos[1])
        target_health = zombie.health
        _add_attack_target(attack_targets, target_pos, target_health)

    for enemy_base in game_map._enemies.values():
        for enemy_block in enemy_base.blocks:
            enemy_pos = enemy_block.point
            target_pos = (enemy_pos[0], enemy_pos[1])
            target_health = enemy_block.health
            _add_attack_target(attack_targets, target_pos, target_health)

    return attack_targets


def get_attack(game_map: map_lib.Map) -> tp.List[models.Attack]:
    attack_targets = _attack_targets(game_map)

    # [target_count, max_hp, x, y]
    targets_sorted_list = ...

    game_map._base

    attack_command: tp.List[models.Attack] = []

    for block_id, block in game_map._base.blocks.items():
        block.distance

    return attack_command

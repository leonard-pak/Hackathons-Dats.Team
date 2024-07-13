import typing as tp

import numpy as np

import map_lib
import models
import utils


AGGRO_CONFIG = {
    'default_zombie_aggro': 1,
    'enemy_aggro': 10,
    'enemy_head_aggro': 50,
    models.ZombieTypes.NORMAL: 1,
    models.ZombieTypes.FAST: 2,
    models.ZombieTypes.BOMBER: 5,
    models.ZombieTypes.LINER: 5,
    models.ZombieTypes.JUGGERNAUT: 4,
    models.ZombieTypes.CHAOS_KNIGHT: 3,
}


def _add_attack_target(attack_targets: tp.Dict, target_pos: tp.Tuple[int, int], target_health: int, aggro: int = 1):
    if target_pos in attack_targets:
        prev_state = attack_targets[target_pos]
        attack_targets[target_pos] = (
            prev_state[0] + aggro, max(prev_state[1], target_health))
    else:
        attack_targets[target_pos] = (aggro, target_health)


def _attack_targets(game_map: map_lib.Map) -> tp.Dict[tp.Tuple[int, int], tp.Tuple[int, int]]:
    # returns Dict[pos[x, y]: [target_count, max_hp]]
    attack_targets = {}

    for zombie in game_map._zombies.values():
        zombie_pos = zombie.point
        target_pos = (int(zombie_pos[0]), int(zombie_pos[1]))
        target_health = zombie.health
        _add_attack_target(attack_targets, target_pos,
                           target_health, AGGRO_CONFIG['zombie_aggro'])

    for enemy_block in game_map._enemies:
        enemy_pos = enemy_block.point
        target_pos = (int(enemy_pos[0]), int(enemy_pos[1]))
        target_health = enemy_block.health
        aggro = AGGRO_CONFIG['enemy_head_aggro'] if enemy_block.attack == 40 else AGGRO_CONFIG['enemy_aggro']
        _add_attack_target(attack_targets, target_pos, target_health, aggro)

    return attack_targets


def get_attack(game_map: map_lib.Map) -> tp.List[models.Attack]:
    attack_targets = _attack_targets(game_map)

    # (target_count, max_hp, x, y)
    targets_sorted = sorted([(-stats[0], stats[1], point[0], point[1])
                            for point, stats in attack_targets.items()])

    attack_command: tp.List[models.Attack] = []

    for block_id, block in game_map._base.blocks.items():
        selected_target = None
        selected_target_idx = None

        distance = block.distance
        for idx, target in enumerate(targets_sorted):
            target_distance = utils.calc_range(
                block.point, np.array([target[-2], target[-1]]))
            if target_distance <= distance:
                selected_target = target
                selected_target_idx = idx
                break

        if not selected_target or not selected_target_idx:
            continue

        damage = block.attack
        remaining_hp = selected_target[1] - damage
        target_x = selected_target[-2]
        target_y = selected_target[-1]
        if remaining_hp <= 0:
            targets_sorted.pop(selected_target_idx)
        else:
            targets_sorted[selected_target_idx] = (
                selected_target[0], remaining_hp, target_x, target_y)
            targets_sorted.sort()

        attack_command.append(models.Attack(
            block_id, models.Point(target_x, target_y)))

    return attack_command

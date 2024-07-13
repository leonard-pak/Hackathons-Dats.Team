import store as s
import numpy as np
import models as m
import itertools as it

SHIFT_BY_DIRECTION: dict[m.ZombieDirection, np.ndarray] = {
    m.ZombieDirection.TOP: np.array([0, -1]),
    m.ZombieDirection.BOTTOM: np.array([0, 1]),
    m.ZombieDirection.RIGHT: np.array([1, 0]),
    m.ZombieDirection.LEFT: np.array([-1, 0]),
}

JUMP_BY_DIRECTION: dict[m.ZombieDirection, np.ndarray] = {
    m.ZombieDirection.RIGHT: np.array([[0, -1], [0, 1]]),
    m.ZombieDirection.LEFT: np.array([[0, -1], [0, 1]]),
    m.ZombieDirection.BOTTOM: np.array([[1, 0], [-1, 0]]),
    m.ZombieDirection.TOP: np.array([[1, 0], [-1, 0]]),
}


def normal(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    return np.array([info.point + SHIFT_BY_DIRECTION[info.direction] * info.speed])


def fast(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    return np.array([info.point + SHIFT_BY_DIRECTION[info.direction] * info.speed])


def bomber(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    next_point = info.point + SHIFT_BY_DIRECTION[info.direction] * info.speed
    x = (0, 1, -1)
    y = (0, 1, -1)
    return np.array([next_point+shift for shift in it.product(x, y)])


def liner(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    return np.array([
        info.point + SHIFT_BY_DIRECTION[info.direction] * (shift+1)
        for shift in range(info.speed)
    ])


def juggernaut(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    return np.array([info.point + SHIFT_BY_DIRECTION[info.direction] * info.speed])


def chaos_knight(info: s.Zombie):
    if (info.waitTurns > 1):
        return np.array([])
    return np.array([
        info.point + SHIFT_BY_DIRECTION[info.direction] * 2 + jump
        for jump in JUMP_BY_DIRECTION[info.direction]
    ])


DAMAGE_BY_ZOMBIE_TYPE = {
    m.ZombieTypes.NORMAL: normal,
    m.ZombieTypes.BOMBER: bomber,
    m.ZombieTypes.FAST: fast,
    m.ZombieTypes.LINER: liner,
    m.ZombieTypes.JUGGERNAUT: juggernaut,
    m.ZombieTypes.CHAOS_KNIGHT: chaos_knight,
}

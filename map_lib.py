from store import Store
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
import enum
import copy
import itertools
import zombie as z


class PointType(int, enum.Enum):
    EMPTY = 0
    ZOMBIE = 1
    ZOMBIE_SPAWN = 2
    WALL = 3
    MY_BASE = 4
    MY_CAPITAL = 5
    ENEMY_BASE = 6
    ENEMY_CAPITAL = 7


class Map():
    DYNAMIC_GROUP = (
        PointType.ZOMBIE,
        PointType.ENEMY_BASE,
        PointType.ENEMY_CAPITAL,
        PointType.MY_BASE,
        PointType.MY_CAPITAL,
    )

    OUR_GROUP = (
        PointType.MY_BASE,
        PointType.MY_CAPITAL,
    )

    ZOMBIE_GROUP = (
        PointType.ZOMBIE,
        PointType.ZOMBIE_SPAWN,
    )

    ENEMY_GROUP = (
        PointType.ENEMY_BASE,
        PointType.ENEMY_CAPITAL,
    )

    def __init__(self, store: Store, reserve_multiplier: int) -> None:
        self._store = store
        self._zombie_spots = self._store.get_spots()
        self._walls = self._store.get_walls()

        self._reserve_multiplier = reserve_multiplier

        self.update()

    def update(self):
        self._store.sync()

        self._static_map = self._build_static_map(
            reserve_multiplier=self._reserve_multiplier,
        )

        self._base = self._store.get_base()
        self._enemies = self._store.get_enemies()
        self._zombies = self._store.get_zombies()
        self._info = self._store.get_game_info()

        self._init_point = self.get_base_center()
        self._map = self._build_map()

    def get_visible_map(self):
        rows, cols = np.where(np.isin(self._map, self.DYNAMIC_GROUP))

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        return self._map[min_row:max_row+1, min_col:max_col+1]

    def get_base_center(self) -> tuple[int, int]:
        if len(self._base.blocks) == 0:
            # return np.array([0, 0])
            raise RuntimeError("We Died!")

        counter = 0
        total_x = 0
        total_y = 0
        for block in self._base.blocks.values():
            block_pos = block.point
            block_pos_x, block_pos_y = int(block_pos[0]), int(block_pos[1])

            counter += 1
            total_x += block_pos_x
            total_y += block_pos_y

        return (round(total_x / counter), round(total_y / counter))

    def get_nearest_spot(self):
        nearest_idx = np.array([np.abs(spot.point - self._init_point).sum()
                                for spot in self._zombie_spots]).argmin()
        return self._zombie_spots[nearest_idx]

    def calc_score2(self, x, y):
        score = 0
        tmp_x = x
        while self.is_our_base(tmp_x, y):
            score += 1
            tmp_x += 1
        tmp_x = x
        while self.is_our_base(tmp_x, y):
            score -= 1
            tmp_x -= 1
        tmp_y = y
        while self.is_our_base(x, tmp_y):
            score += 1
            tmp_y += 1
        tmp_y = y
        while self.is_our_base(x, tmp_y):
            score -= 1
            tmp_y -= 1
        return score

    def find_save_point3(self):
        damage_map = np.zeros(np.shape(self._map))
        for zombie in self._zombies.values():
            points = z.DAMAGE_BY_ZOMBIE_TYPE[zombie.type](zombie)
            for point in points:
                damage_map[point[0]][point[1]] += zombie.attack * 100

        min_damage = 1e10
        min_x = 0
        min_y = 0
        success = False

        for x in range(np.shape(damage_map)[0]):
            for y in range(np.shape(damage_map)[1]):
                if self.is_our_base(x, y):
                    damage_map[point[0]][point[1]] += self.calc_score2(x, y)
                    if damage_map[point[0]][point[1]] < min_damage:
                        min_damage = damage_map[point[0]][point[1]]
                        min_x = x
                        min_y = y
                        success = True

        return (min_x, min_y) if success else None

    def get_neighbours_count(self, x: int, y: int) -> int:
        counter = 0
        x_max, y_max = self._map.shape
        for delta_x in range(-2, 3):
            for delta_y in range(-2, 3):
                if self.is_our_base(max(min(x + delta_x, x_max), 0), max(min(y + delta_y, y_max), 0)):
                    counter += 1
        return counter

    def count_cost(self, x: int, y: int, cache, is_visited):
        if not self.is_our_base(x, y):
            return 0
        if is_visited[x][y]:
            return cache[x][y]
        is_visited[x][y] = True
        return 1 + \
            self.count_cost(x + 1, y, cache, is_visited) + \
            self.count_cost(x, y + 1, cache, is_visited) + \
            self.count_cost(x - 1, y, cache, is_visited) + \
            self.count_cost(x, y - 1, cache, is_visited)

    def find_save_point2(self):
        damage_map = np.zeros(np.shape(self._map))
        cache = [[0]*np.shape(self._map)[1]]*np.shape(self._map)[0]
        is_visited = [[False]*np.shape(self._map)[1]]*np.shape(self._map)[0]

        max_cost = 0
        min_x = 0
        min_y = 0
        success = False
        for x in range(np.shape(damage_map)[0]):
            for y in range(np.shape(damage_map)[1]):
                if not self.is_our_base(x, y):
                    continue

                cost = self.count_cost(
                    x, y, cache=cache, is_visited=is_visited)
                cache[x][y] = cost
                is_visited[x][y] = True
                if cost > max_cost:
                    max_cost = cost
                    min_x = x
                    min_y = y
                    success = True

        return (min_x, min_y) if success else None

    def find_save_point(self):
        damage_map = np.zeros(np.shape(self._map))
        for zombie in self._zombies.values():
            points = z.DAMAGE_BY_ZOMBIE_TYPE[zombie.type](zombie)
            for point in points:
                damage_map[point[0]][point[1]] = zombie.attack * 100

        center_x, center_y = self._init_point

        for i in range(np.shape(damage_map)[0]):
            for j in range(np.shape(damage_map)[1]):
                x_coords = [
                    min(i+3, np.shape(self._map)[0] - 1),
                    min(i+2, np.shape(self._map)[0] - 1),
                    min(i+1, np.shape(self._map)[0] - 1),
                    i,
                    max(i-1, 0),
                    max(i-2, 0),
                    max(i-3, 0),
                ]
                y_coords = [
                    min(j+3, np.shape(self._map)[1] - 1),
                    min(j+2, np.shape(self._map)[1] - 1),
                    min(j+1, np.shape(self._map)[1] - 1),
                    j,
                    max(j-1, 0),
                    max(j-2, 0),
                    max(j-3, 0),
                ]
                value = sum(
                    self._map[x][y] in self.OUR_GROUP
                    for x, y in itertools.product(x_coords, y_coords)
                )
                damage_map[i][j] -= value
                # dist = abs(center_x - i) + abs(center_y - i)
                # damage_map[i][j] += dist * 5

        min_damage = 1e10
        min_x = 0
        min_y = 0
        success = False
        for i in range(np.shape(damage_map)[0]):
            for j in range(np.shape(damage_map)[1]):
                x_coords = [
                    min(i+5, np.shape(self._map)[0] - 1),
                    min(i+4, np.shape(self._map)[0] - 1),
                    min(i+3, np.shape(self._map)[0] - 1),
                    min(i+2, np.shape(self._map)[0] - 1),
                    min(i+1, np.shape(self._map)[0] - 1),
                    i,
                    max(i-1, 0),
                    max(i-2, 0),
                    max(i-3, 0),
                    max(i-4, 0),
                    max(i-5, 0),
                ]
                y_coords = [
                    min(j+5, np.shape(self._map)[1] - 1),
                    min(j+4, np.shape(self._map)[1] - 1),
                    min(j+3, np.shape(self._map)[1] - 1),
                    min(j+2, np.shape(self._map)[1] - 1),
                    min(j+1, np.shape(self._map)[1] - 1),
                    j,
                    max(j-1, 0),
                    max(j-2, 0),
                    max(j-3, 0),
                    max(j-4, 0),
                    max(j-5, 0),
                ]
                value = sum(
                    self._map[x][y] in self.OUR_GROUP
                    for x, y in itertools.product(x_coords, y_coords)
                )
                if self.is_our_base(i, j) and damage_map[i][j] - value < min_damage:
                    min_damage = damage_map[i][j] - value
                    min_x = i
                    min_y = j
                    success = True

        return (min_x, min_y) if success else None

    def is_point_available_to_build(self, x: int, y: int, turn: int = 1, turn_break: int = 50):
        # В отрицательную зону нельзя
        if x < 0 or y < 0:
            return False
        # Не на своей базе
        if self._map[x][y] in self.OUR_GROUP:
            return False
        # Не на зомби или споте
        # if self._map[x][y] in self.ZOMBIE_GROUP:
        #     return False
        x_coords = [
            min(x+1, np.shape(self._map)[0]),
            x,
            max(x-1, 0),
        ]
        y_coords = [
            min(y+1, np.shape(self._map)[1]),
            y,
            max(y-1, 0),
        ]
        # Должны прижаты к своей базе
        # if not any(
        #     self._map[x][y] in self.OUR_GROUP
        #     for x, y in itertools.product(x_coords, y_coords)
        # ):
        #     return False
        if turn > turn_break:
            x_coords = [
                # min(x+5, np.shape(self._map)[0]),
                # min(x+4, np.shape(self._map)[0]),
                # min(x+3, np.shape(self._map)[0]),
                min(x+2, np.shape(self._map)[0]),
                min(x+1, np.shape(self._map)[0]),
                x,
                max(x-1, 0),
                max(x-2, 0),
                # max(x-3, 0),
                # max(x-4, 0),
                # max(x-5, 0),
            ]
            y_coords = [
                # min(y+5, np.shape(self._map)[1]),
                # min(y+4, np.shape(self._map)[1]),
                # min(y+3, np.shape(self._map)[1]),
                min(y+2, np.shape(self._map)[1]),
                min(y+1, np.shape(self._map)[1]),
                y,
                max(y-1, 0),
                max(y-2, 0),
                # max(y-3, 0),
                # max(y-4, 0),
                # max(y-5, 0),
            ]
        # Не прижаты к споту
        if any(
            self._map[x][y] == PointType.ZOMBIE_SPAWN
            for x, y in itertools.product(x_coords, y_coords)
        ):
            return False
        x_coords = [
            min(x+1, np.shape(self._map)[0]),
            x,
            max(x-1, 0),
        ]
        y_coords = [
            min(y+1, np.shape(self._map)[1]),
            y,
            max(y-1, 0),
        ]
        # Далеко от врагов
        x_coords.append(x)
        y_coords.append(y)
        if any(
            self._map[x][y] in self.ENEMY_GROUP
            for x, y in itertools.product(x_coords, y_coords)
        ):
            return False

        return True

    def is_our_base(self, x: int, y: int):
        return self._map[x][y] in self.OUR_GROUP

    def _build_static_map(self, reserve_multiplier: int):
        points = list[npt.NDArray[np.int32]]()
        types = list[PointType]()
        for spot in self._zombie_spots:
            points.append(spot.point)
            types.append(PointType.ZOMBIE_SPAWN)
        for wall in self._walls:
            points.append(wall.point)
            types.append(PointType.WALL)
        points = np.array(points)
        scales = np.round(
            (points.max(axis=0) + 1) * reserve_multiplier).astype(int)
        static_map = np.zeros((scales[0] + 30, scales[1] + 30))
        for point_coord, point_type in zip(points, types):
            idxes = point_coord
            static_map[idxes[0]][idxes[1]] = point_type
        return static_map

    def _build_map(self):
        map = copy.deepcopy(self._static_map)
        # Наша база
        for block_id, block_info in self._base.blocks.items():
            map[block_info.point[0]][block_info.point[1]
                                     ] = PointType.MY_CAPITAL if block_id == self._base.head_key else PointType.MY_BASE
        # Базы врагов
        for enemy_block in self._enemies:
            map[enemy_block.point[0]][enemy_block.point[1]
                                      ] = PointType.ENEMY_CAPITAL if enemy_block.is_head else PointType.ENEMY_BASE

        # Зомби
        for zombie_info in self._zombies.values():
            map[zombie_info.point[0]][zombie_info.point[1]] = PointType.ZOMBIE
        return map

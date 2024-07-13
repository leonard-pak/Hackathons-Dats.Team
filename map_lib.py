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

        self._static_map = self._build_static_map(
            reserve_multiplier=reserve_multiplier
        )

        self.update()

    def update(self):
        self._store.sync()
        self._base = self._store.get_base()
        self._enemies = self._store.get_enemies()
        self._zombies = self._store.get_zombies()
        self._info = self._store.get_game_info()

        self._init_point = self.get_base_center()
        self.__map = self._build_map()

    def get_visible_map(self):
        rows, cols = np.where(np.isin(self.__map, self.DYNAMIC_GROUP))

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        return self.__map[min_row:max_row+1, min_col:max_col+1]

    def get_base_center(self) -> npt.NDArray[np.int32]:
        if len(self._base.blocks) == 0:
            # return np.array([0, 0])
            raise RuntimeError("We Died!")

        return np.array([block.point for _, block in self._base.blocks.items()]).mean(axis=1)

    def get_nearest_spot(self):
        nearest_idx = np.array([np.abs(spot.point - self._init_point).sum()
                                for spot in self._zombie_spots]).argmin()
        return self._zombie_spots[nearest_idx]

    def get_neighbours_count(self, x: int, y: int) -> int:
        counter = 0
        x_max, y_max = self.__map.shape
        for delta_x in range(-2, 3):
            for delta_y in range(-2, 3):
                if self.is_our_base(max(min(x + delta_x, x_max), 0), max(min(y + delta_y, y_max), 0)):
                    counter += 1
        return counter

    def find_save_point(self):
        damage_map = np.zeros(np.shape(self.__map))
        for zombie in self._zombies.values():
            points = z.DAMAGE_BY_ZOMBIE_TYPE[zombie.type](zombie)
            for point in points:
                damage_map[point[0]][point[1]] = 1 / zombie.attack

        mask = np.isin(self.__map, self.OUR_GROUP)
        damage_map[mask] = 0
        i = damage_map.argmax()
        return i // np.shape(damage_map)[0], i % np.shape(damage_map)[0]

    def is_point_available_to_build(self, x: int, y: int, turn: int = 1, turn_break: int = 50):
        # В отрицательную зону нельзя
        if x < 0 or y < 0:
            return False
        # Не на своей базе
        if self.__map[x][y] in self.OUR_GROUP:
            return False
        # Не на зомби или споте
        if self.__map[x][y] in self.ZOMBIE_GROUP:
            return False
        x_coords = [
            min(x+1, np.shape(self.__map)[0]),
            max(x-1, 0),
        ]
        y_coords = [
            min(y+1, np.shape(self.__map)[1]),
            max(y-1, 0),
        ]
        # Должны прижаты к своей базе
        if not any(
            self.__map[x][y] in self.OUR_GROUP
            for x, y in itertools.product(x_coords, y_coords)
        ):
            return False
        if turn > turn_break:
            x_coords = [
                # min(x+5, np.shape(self.__map)[0]),
                # min(x+4, np.shape(self.__map)[0]),
                min(x+3, np.shape(self.__map)[0]),
                min(x+2, np.shape(self.__map)[0]),
                min(x+1, np.shape(self.__map)[0]),
                max(x-1, 0),
                max(x-2, 0),
                max(x-3, 0),
                # max(x-4, 0),
                # max(x-5, 0),
            ]
            y_coords = [
                # min(y+5, np.shape(self.__map)[1]),
                min(y+4, np.shape(self.__map)[1]),
                min(y+3, np.shape(self.__map)[1]),
                min(y+2, np.shape(self.__map)[1]),
                min(y+1, np.shape(self.__map)[1]),
                max(y-1, 0),
                max(y-2, 0),
                max(y-3, 0),
                max(y-4, 0),
                # max(y-5, 0),
            ]
        # Не прижаты к споту
        if any(
            self.__map[x][y] == PointType.ZOMBIE_SPAWN
            for x, y in itertools.product(x_coords, y_coords)
        ):
            return False
        x_coords = [
            min(x+1, np.shape(self.__map)[0]),
            max(x-1, 0),
        ]
        y_coords = [
            min(y+1, np.shape(self.__map)[1]),
            max(y-1, 0),
        ]
        # Далеко от врагов
        x_coords.append(x)
        y_coords.append(y)
        if any(
            self.__map[x][y] in self.ENEMY_GROUP
            for x, y in itertools.product(x_coords, y_coords)
        ):
            return False

        return True

    def is_our_base(self, x: int, y: int):
        return self.__map[x][y] in self.OUR_GROUP

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

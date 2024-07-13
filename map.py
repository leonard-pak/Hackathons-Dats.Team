from store import Store
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
import enum
import copy


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
    def __init__(self, store: Store, reserve_multiplier: int) -> None:
        self._store = store
        self._zombie_spots = self._store.get_spots()
        self._walls = self._store.get_walls()

        self._static_map, self._map_shift = self._build_static_map(
            reserve_multiplier=reserve_multiplier)

        self.update()
        self._init_point = self.get_base_center()

    def update(self):
        self._base = self._store.get_base()
        # TODO Дополучать всё остальное на карту

        self._map = copy.deepcopy(self._static_map)
        for block_id, block_info in self._base.blocks.items():
            self._add_to_map(block_info.point[0], block_info.point[1],
                             PointType.MY_CAPITAL if block_id == self._base.head else PointType.MY_BASE)

    def _add_to_map(self, x: int, y: int, info: PointType):
        self._map[x + self._map_shift][y + self._map_shift] = info

    def get_base_center(self) -> npt.NDArray[np.int32]:
        return np.array([block.point for _, block in self._base.blocks.items()]).mean(axis=1)

    def get_nearest_spot(self):
        nearest_idx = np.array([np.abs(spot.point - self._init_point).sum()
                                for spot in self._zombie_spots]).argmin()
        return self._zombie_spots[nearest_idx]

    def is_point_available(self, x: int, y: int):
        # TODO проверять в соотвествие с правилами
        pass

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
        max_x_y: npt.NDArray[np.int32] = points.max(axis=0)
        min_x_y: npt.NDArray[np.int32] = points.min(axis=0)
        scales = (max_x_y - min_x_y) * reserve_multiplier
        map_idx_shifts = (scales - max_x_y - min_x_y) / 2
        # TODO В какую сторону лучше округлять? Уже засыпаю
        map_idx_shifts = np.round(map_idx_shifts).astype(int)
        static_map = np.zeros((scales[0], scales[1]))
        for point_coord, point_type in zip(points, types):
            idxes = point_coord + map_idx_shifts
            static_map[idxes[0]][idxes[1]] = point_type
        return static_map, map_idx_shifts

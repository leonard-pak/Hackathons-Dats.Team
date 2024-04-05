import typing as tp

import numpy as np

import garbage


ACTION_STEPS = [
    [-1, -1],
    [-1, 0],
    [0, -1],
    [1, -1],
]


def _index_figure(figure):
    return figure[:, 0], figure[:, 1]


def _rotate_90(figure, times: int, shift: tp.Tuple = (0, 0)):
        return figure @ np.linalg.matrix_power(np.array([
            [0, -1],
            [1, 0],
        ]), times).astype(np.int_) + shift


def _calc_figure_area(figure) -> int:
    return figure.shape[0]


def _calc_figure_bbox_area(figure) -> int:
    return np.prod(figure.max(axis=0) - figure.min(axis=0) + 1)


def _sort_function(figure) -> tp.Tuple[int, int]:
    # returns (Free space, Area)
    area = _calc_figure_area(figure)
    bbox_area = _calc_figure_bbox_area(figure)
    return (bbox_area - area, area)


class Packager():
    def __init__(self, capacity_x: int, capacity_y: int, garbage_list: tp.List[garbage.GarbageItem]) -> None:
        self.capacity_x = capacity_x
        self.capacity_y = capacity_y

        self.occupancy_map = self._calc_occupancy_map()
        self.distance_map = self._calc_distance_map()

        self.garbage_list = self._sort_garbages(garbage_list)
        self.packed_garbages: tp.List[garbage.GarbageItem] = []

    def _pack_garbage(self, garbage: garbage.GarbageItem):
        self.packed_garbages.append(garbage)
        self.garbage_list.remove(garbage)

        self.occupancy_map = self._calc_occupancy_map()
        self.distance_map = self._calc_distance_map()

    def _calc_occupancy_map(self):
        occupancy_map = np.zeros(self.capacity_x * self.capacity_y).reshape(self.capacity_y, self.capacity_x).astype(np.int_)
        for garbage in self.packed_garbages:
            occupancy_map[_index_figure(garbage)] = 1
        return occupancy_map

    def _calc_distance_map(self):
        distance_map = np.zeros_like(self.occupancy_map)
        for dy in range(self.capacity_y):
            for dx in range(self.capacity_x):
                if self.occupancy_map[dy, dx] == 1:
                    continue
                distance_map[dy, dx] = min(
                    distance_map[dy - 1, dx] + 1,
                    distance_map[dy, dx - 1] + 1,
                )
        return distance_map

    def _move_to_corner(self, figure):
        return figure + [self.capacity_y - np.max(figure[:, 0]) - 1, self.capacity_x - np.max(figure[:, 1]) - 1]

    def _is_valid_position(self, figure) -> bool:
        for coord_y, coord_x in figure:
            if not 0 <= coord_y < self.capacity_y or not 0 <= coord_x < self.capacity_x:
                return False
            if self.occupancy_map[coord_y, coord_x] == 1:
                return False
        return True

    def _calc_figure_cost(self, figure) -> int:
        coord_set = set((coord[0], coord[1]) for coord in figure)
        return sum(self.distance_map[coord_y, coord_x] for coord_y, coord_x in coord_set)

    def _find_local_optimal_pos(self, figure):
        optimal_pos = None
        current_pos = self._move_to_corner(figure)
        while True:
            optimal_step = [0, 0]
            optimal_cost = float('inf')
            if self._is_valid_position(current_pos):
                optimal_cost = self._calc_figure_cost(current_pos)
            for step in ACTION_STEPS:
                possible_pos = current_pos + step
                if not self._is_valid_position(possible_pos):
                    continue
                possible_cost = self._calc_figure_cost(possible_pos)
                if possible_cost <= optimal_cost:
                    optimal_step = step
                    optimal_cost = possible_cost

            if optimal_step == [0, 0]:
                break
            current_pos += optimal_step

        if optimal_cost != float('inf'):
            optimal_pos = current_pos

        return optimal_pos, optimal_cost

    def _find_optimal_pos(self, figure):
        init_pos = np.copy(figure)

        optimal_pos = None
        optimal_cost = float('inf')
        for rotate in range(4):
            current_pos = _rotate_90(init_pos, rotate)
            local_optimal_pos, local_optimal_cost = self._find_local_optimal_pos(current_pos)

            if local_optimal_pos is None:
                continue
            if local_optimal_cost < optimal_cost:
                optimal_pos = local_optimal_pos
                optimal_cost = local_optimal_cost

        return optimal_pos

    def _sort_garbages(self, garbage_list: tp.List[garbage.GarbageItem]) -> tp.List[garbage.GarbageItem]:
        return sorted(garbage_list, key=_sort_function)

    def pack_garbages(self) -> tp.List[garbage.GarbageItem]:
        for garbage in self.garbage_list:
            packager_coords = np.flip(garbage.form)
            optimal_pos = self._find_optimal_pos(packager_coords)
            if optimal_pos is None:
                continue

            self._pack_garbage(garbage)

        return self.packed_garbages


def optimal_packing(capacity_x: int, capacity_y: int, garbage_list: tp.List[garbage.GarbageItem]) -> tp.List[garbage.GarbageItem]:
    packager = Packager(capacity_x, capacity_y, garbage_list)
    return packager.pack_garbages()

from store import Store
import numpy as np
import numpy.typing as npt


class Map():
    def __init__(self, store: Store) -> None:
        self._store = store
        self._zombie_spots = self._store.get_spots()
        self._walls = self._store.get_walls()
        self.update()
        self._init_point = self.get_base_center()

    def update(self):
        self._base = self._store.get_base()

    def get_base_center(self) -> npt.NDArray[np.int32]:
        return np.array([block.point for _, block in self._base.blocks.items()]).mean(axis=1)

    def get_nearest_spot(self):
        nearest_idx = np.array([np.abs(spot.point - self._init_point).sum()
                                for spot in self._zombie_spots]).argmin()
        return self._zombie_spots[nearest_idx]

import typing as tp


GarbageItemT = tp.List[tp.Tuple[int, int]]
GarbageT = tp.Dict[str, GarbageItemT]


class GarbageItem():
    def __init__(self, name: str, form: GarbageItemT) -> None:
        self.name = name
        self.form = form


class Storage():
    def __init__(self, capacity_x: int, capacity_y: int, garbage_items: tp.List[GarbageItem]) -> None:
        self.capacity_x = capacity_x
        self.capacity_y = capacity_y
        self.garbage_items = garbage_items


class Ship():
    def __init__(self, capacity_x: int, capacity_y: int, fuel_used: int, storage: Storage) -> None:
        self.capacity_x = capacity_x
        self.capacity_y = capacity_y
        self.fuel_used = fuel_used
        self.storage = storage

    @classmethod
    def create(cls, capacity_x: int, capacity_y: int, fuel_used: int, storage: tp.Dict) -> 'Ship':
        ...

    def update(self):
        ...

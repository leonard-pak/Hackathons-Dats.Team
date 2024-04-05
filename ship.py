import typing as tp


GarbageItemT = tp.List[tp.Tuple[int, int]]

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
    def create(cls, record) -> 'Ship':
        garbages = [GarbageItem(name, [(point[0], point[1]) for point in form]) for [name, form] in record['ship']['garbage']]
        storage = Storage(record['ship']['capacityX'], record['ship']['capacityY'], garbages)
        return cls(record['ship']['capacityX'], record['ship']['capacityY'], record['ship']['fuelUsed'], storage)

    def update(self):
        ...

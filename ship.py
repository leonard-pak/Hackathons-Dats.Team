import typing as tp

from garbage import GarbageItem

class Storage():
    def __init__(self, capacity_x: int, capacity_y: int, garbage_items: tp.List[GarbageItem]) -> None:
        self.capacity_x = capacity_x
        self.capacity_y = capacity_y
        self.garbage_items = garbage_items

    @classmethod
    def create(cls, record) -> 'Storage':
        garbages = GarbageItem.createList(record['garbage'])
        return cls(record['capacityX'], record['capacityY'], garbages)

class Ship():
    def __init__(self, fuel_used: int, storage: Storage) -> None:
        self.fuel_used = fuel_used
        self.storage = storage

    @classmethod
    def create(cls, record) -> 'Ship':
        storage = Storage.create(record)
        return cls(record['fuelUsed'], storage)

    def update(self):
        ...

import typing as tp

GarbageItemT = tp.List[tp.Tuple[int, int]]

class GarbageItem():
    def __init__(self, name: str, form: GarbageItemT) -> None:
        self.name = name
        self.form = form

    @classmethod
    def createList(cls, record):
        return [cls(name, [(point[0], point[1]) for point in form]) for [name, form] in record]

import dataclasses
import enum
import typing as tp


@dataclasses.dataclass
class BaseModel():
    def to_record(self) -> tp.Dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Point(BaseModel):
    x: int
    y: int


@dataclasses.dataclass
class Attack(BaseModel):
    block_id: str
    target: Point


@dataclasses.dataclass
class Build(BaseModel):
    point: Point


@dataclasses.dataclass
class MoveBase(Point):
    ...


@dataclasses.dataclass
class BaseItem(BaseModel):
    attack: int
    health: int
    id: str
    isHead: bool
    last_attack: Point
    range: int
    x: int
    y: int

    @classmethod
    def _parse_record(cls, record: tp.Dict) -> 'BaseItem':
        last_attack = record['last_attack']
        return cls(

        )

    @classmethod
    def from_list_record(cls, records: tp.List[tp.Dict]) -> tp.List['BaseItem']:
        return []

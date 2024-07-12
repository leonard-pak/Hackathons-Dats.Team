import dataclasses
import enum
import typing as tp


@dataclasses.dataclass
class BaseModel():
    def to_record(self) -> tp.Dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_record(cls, record: tp.Dict) -> 'BaseModel':
        return cls(**record)

    @classmethod
    def from_list_record(cls, records: tp.List[tp.Dict]) -> tp.List['BaseModel']:
        return [cls.from_record(record) for record in records]


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
    def from_record(cls, record: tp.Dict) -> 'BaseItem':
        last_attack = record.pop('last_attack')
        record['last_attack'] = Point(**last_attack)
        return cls(**record)


@dataclasses.dataclass
class EnemyBaseItem(BaseModel):
    attack: int
    health: int
    isHead: bool
    last_attack: Point
    name: str
    x: int
    y: int

    @classmethod
    def from_record(cls, record: tp.Dict) -> 'EnemyBaseItem':
        last_attack = record.pop('last_attack')
        record['last_attack'] = Point(**last_attack)
        return cls(**record)


@dataclasses.dataclass
class Player(BaseModel):
    enemy_block_kills: int
    game_ended_at: str
    gold: int
    name: str
    points: int
    zombie_kills: int


@dataclasses.dataclass
class Zombie(BaseModel):
    attack: int
    direction: str
    health: int
    id: str
    speed: int
    type: str
    wait_turns: int
    x: int
    y: int


@dataclasses.dataclass
class RealmName(BaseModel):
    realm_name: str


@dataclasses.dataclass
class Turn(BaseModel):
    turn: int


@dataclasses.dataclass
class TurnEndsInMs(BaseModel):
    turn_ends_in_ms: int


@dataclasses.dataclass
class ZombieSpot(BaseModel):
    x: int
    x: int
    type: str


@dataclasses.dataclass
class Round(BaseModel):
    duration: int
    end_at: str
    name: str
    repeat: int
    start_at: str
    status: str

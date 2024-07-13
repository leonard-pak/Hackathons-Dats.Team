import datetime as dt
import dataclasses
import enum
import typing as tp
import uuid

import utils

BaseModelT = tp.TypeVar('BaseModelT', bound='BaseModel')


@dataclasses.dataclass
class BaseModel():
    def to_record(self) -> tp.Dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_record(cls: tp.Type[BaseModelT], record: tp.Dict) -> 'BaseModelT':
        return cls(**record)

    @classmethod
    def from_list_record(cls: tp.Type[BaseModelT], records: tp.List[tp.Dict]) -> tp.List['BaseModelT']:
        if not records:
            return []
        return [cls.from_record(record) for record in records]


@dataclasses.dataclass
class Point(BaseModel):
    x: int
    y: int


@dataclasses.dataclass
class Attack(BaseModel):
    blockId: str
    target: Point

    def to_record(self) -> tp.Dict:
        return {
            'blockId': self.blockId,
            'target': {
                'x': self.target.x,
                'y': self.target.y,
            }
        }


@dataclasses.dataclass
class Build(BaseModel):
    point: Point

    def to_record(self) -> tp.Dict:
        return {
            'x': self.point.x,
            'y': self.point.y,
        }


@dataclasses.dataclass
class MoveBase(Point):
    ...

    def to_record(self) -> tp.Dict:
        return {
            'x': self.x,
            'y': self.y,
        }


@dataclasses.dataclass
class BaseItem(BaseModel):
    attack: int
    health: int
    id: str
    last_attack: tp.Optional[Point]
    range: int
    x: int
    y: int
    isHead: bool = False

    def __post_init__(self):
        self.isHead = self.attack == 40

    @classmethod
    def from_record(cls, record: tp.Dict) -> 'BaseItem':
        last_attack = record.pop('lastAttack')
        if last_attack is None:
            record['last_attack'] = None
        else:
            record['last_attack'] = Point(**last_attack)
        return cls(**record)


@dataclasses.dataclass
class EnemyBaseItem(BaseModel):
    attack: int
    health: int
    last_attack: tp.Optional[Point]
    x: int
    y: int
    isHead: bool = False
    # name: str = dataclasses.field(default_factory=lambda: str(uuid.uuid1()))
    # name: str = '111'

    def __post_init__(self):
        self.isHead = self.attack == 40

    @classmethod
    def from_record(cls, record: tp.Dict) -> 'EnemyBaseItem':
        last_attack = record.pop('lastAttack')
        if last_attack is None:
            record['last_attack'] = None
        else:
            record['last_attack'] = Point(**last_attack)
        return cls(**record)


@dataclasses.dataclass
class Player(BaseModel):
    enemyBlockKills: int
    gameEndedAt: str
    gold: int
    name: str
    points: int
    zombieKills: int

    def __post_init__(self):
        self.game_ended_at = utils.str_to_datetime(self.gameEndedAt)


class ZombieTypes(str, enum.Enum):
    NORMAL = 'normal'
    FAST = 'fast'
    BOMBER = 'bomber'
    LINER = 'liner'
    JUGGERNAUT = 'juggernaut'
    CHAOS_KNIGHT = 'chaos_knight'


class ZombieDirection(str, enum.Enum):
    TOP = 'up'
    BOTTOM = 'down'
    RIGHT = 'right'
    LEFT = 'left'


@dataclasses.dataclass
class Zombie(BaseModel):
    attack: int
    direction: ZombieDirection
    health: int
    id: str
    speed: int
    type: ZombieTypes
    waitTurns: int
    x: int
    y: int


@dataclasses.dataclass
class RealmName(BaseModel):
    realmName: str


@dataclasses.dataclass
class Turn(BaseModel):
    turn: int


@dataclasses.dataclass
class TurnEndsInMs(BaseModel):
    turnEndsInMs: int


@dataclasses.dataclass
class ZombieSpot(BaseModel):
    x: int
    y: int
    type: str = 'default'


@dataclasses.dataclass
class Wall(BaseModel):
    x: int
    y: int
    type: str = 'wall'


@dataclasses.dataclass
class Round(BaseModel):
    duration: int
    endAt: str
    startAt: str
    name: str
    status: str
    repeat: int = 0

    def __post_init__(self):
        self.end_at = utils.str_to_datetime(self.endAt)
        self.start_at = utils.str_to_datetime(self.startAt)

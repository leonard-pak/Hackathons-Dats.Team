from client import Client
import models as m
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt


@dataclass
class Spot:
    point: npt.NDArray[np.int32]


@dataclass
class Wall:
    point: npt.NDArray[np.int32]


@dataclass
class BaseBlock:
    # last_atack, id, isHead не используются
    point: npt.NDArray[np.int32]
    attack: int
    health: int
    distance: int


@dataclass
class Base:
    blocks: dict[str, BaseBlock]  # key = id
    head: str


class Store:
    def __init__(self, client: Client) -> None:
        self._client = client
        # Вызываем один раз за весь раунд. Не меняется
        world_record = self._client.get_world()
        self._spots = [m.ZombieSpot.from_record(
            record) for record in world_record['zspots'] if record['type'] == m.ZombieSpot.type]
        self._walls = [m.Wall.from_record(
            record) for record in world_record['zspots'] if record['type'] == m.Wall.type]
        # TODO не используется
        self._round_name = m.RealmName.from_record(
            world_record['realmName'])

    def sync(self):
        turn_info = self._client.get_units()
        self._base = m.BaseItem.from_list_record(turn_info['base'])
        # TODO не используется
        self._enemies = m.EnemyBaseItem.from_list_record(
            turn_info['enemyBlocks'])
        # TODO не используется
        self._player = m.Player.from_record(turn_info['player'])
        # TODO не используется
        self._last_round_name = m.RealmName.from_record(
            turn_info['realmName'])
        # TODO не используется
        self._turn = m.Turn.from_record(
            turn_info['turn'])
        # TODO не используется
        self._ms_to_end = m.TurnEndsInMs.from_record(
            turn_info['turnEndsInMs'])
        # TODO не используется
        self._zombies = m.Zombie.from_list_record(turn_info['zombies'])

    def get_spots(self):
        return [Spot(point=np.array([spot.x, spot.y])) for spot in self._spots]

    def get_walls(self):
        return [Wall(point=np.array([wall.x, wall.y])) for wall in self._walls]

    def get_base(self):
        base = Base(blocks=dict(), head='')
        for item in self._base:
            if item.isHead:
                base.head = item.id
            base_block = BaseBlock(point=np.array(
                [item.x, item.y]), attack=item.attack, health=item.health, distance=item.range)
            base.blocks[item.id] = base_block
        return base

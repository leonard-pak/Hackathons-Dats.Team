import dataclasses
import random
import typing as tp

import models
import visualize


random.seed(0)

ZombieT = tp.TypeVar('models.ZombieT', bound='Zombie')


SHIFT_BY_DIRECTION: tp.Dict[models.ZombieDirection, tp.Tuple[int, int]] = {
    models.ZombieDirection.TOP: (0, -1),
    models.ZombieDirection.BOTTOM: (0, 1),
    models.ZombieDirection.RIGHT: (1, 0),
    models.ZombieDirection.LEFT: (-1, 0),
}

COLLIDE_OBJECTS = {
    visualize.MapNumbers.ZOMBIE_SPAWN.value,
    visualize.MapNumbers.WALL.value,
    visualize.MapNumbers.ENEMY_BASE.value,
    visualize.MapNumbers.ENEMY_CAPITAL.value,
    visualize.MapNumbers.MY_BASE.value,
    visualize.MapNumbers.MY_CAPITAL.value,
}


@dataclasses.dataclass
class Zombie(models.Zombie):
    is_destroyed = True

    @classmethod
    def from_type(cls: tp.Type[ZombieT], zombie_type: models.ZombieTypes, **kwargs) -> 'ZombieT':
        # if zombie_type == models.ZombieTypes.NORMAL:
        #     return ZombieNormal(**kwargs)
        return ZombieNormal(**kwargs)

    def _move(self, game_map) -> tp.Tuple[int, int]:
        if self.wait_turns > 0:
            self.wait_turns -= 1
            return self.x, self.y

        x_diff, y_diff = SHIFT_BY_DIRECTION[self.direction]
        for step in range(self.speed):
            cur_x = self.x + x_diff
            cur_y = self.y + y_diff
            map_point: int = game_map[cur_x][cur_y]
            if map_point in COLLIDE_OBJECTS:
                break

        self.x, self.y = cur_x, cur_y
        return self.x, self.y

    def process_round(self, game_map) -> tp.Tuple[int, int]:  # returns end position (x, y)
        return self._move(game_map)


class ZombieNormal(Zombie):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.speed = 1
        self.is_destroyed = True


class ZombieSpot(models.ZombieSpot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.spawn_probability = 0.01
        self.frequency = 10

        self.spawn_probability = 1
        self.frequency = 1

        self._turns_to_spawn = 0
        self._max_probability = 1

        self._possible_directions: tp.List[models.ZombieDirection] = list()
        self._spawned_zombies = 0

    def _increase_probability(self, step: float) -> None:
        self.spawn_probability = min(self.spawn_probability + step, self._max_probability)

    def _increase_frequency(self, step: int) -> None:
        self.frequency = max(self.frequency - step, 1)

    def _calculate_stats(self, turn_number: int) -> tp.Tuple[int, int]:
        base_attack = 5
        base_health = 5
        return base_attack, base_health

    def _spawn_zombie(self, turn_number: int) -> models.Zombie:
        attack, health = self._calculate_stats(turn_number)
        self._spawned_zombies += 1
        zombie_type = random.choice([zombie_type for zombie_type in models.ZombieTypes])
        direction = random.choice(self._possible_directions)
        x_diff, y_diff = SHIFT_BY_DIRECTION[direction]
        return Zombie.from_type(
            zombie_type,
            attack=attack,
            direction=direction,
            health=health,
            id=f'x{self.x}_y{self.y}_id{self._spawned_zombies}',
            speed=1,
            type=zombie_type,
            wait_turns=1,
            x=self.x + x_diff,
            y=self.y + y_diff,
        )

    def init_possible_directions(self, game_map) -> None:
        if game_map[self.x][self.y - 1] != visualize.MapNumbers.ZOMBIE_SPAWN.value:
            self._possible_directions.append(models.ZombieDirection.TOP)
        if game_map[self.x][self.y + 1] != visualize.MapNumbers.ZOMBIE_SPAWN.value:
            self._possible_directions.append(models.ZombieDirection.BOTTOM)
        if game_map[self.x + 1][self.y] != visualize.MapNumbers.ZOMBIE_SPAWN.value:
            self._possible_directions.append(models.ZombieDirection.RIGHT)
        if game_map[self.x - 1][self.y] != visualize.MapNumbers.ZOMBIE_SPAWN.value:
            self._possible_directions.append(models.ZombieDirection.LEFT)

    def process_round(self, turn_number: int) -> tp.Optional[Zombie]:
        self._increase_probability(0.0016388)
        if turn_number % 20 == 0:
            self._increase_frequency(1)

        if self._turns_to_spawn == 0:
            self._turns_to_spawn = self.frequency

            roll = random.random()
            if roll <= self.spawn_probability:
                return self._spawn_zombie(turn_number)

        self._turns_to_spawn -= 1

import enum

import matplotlib.colors as mpl_col
import matplotlib.pyplot as plt
import numpy as np


# Определяем разные типы объектов на карте
class MapNumbers(int, enum.Enum):
    EMPTY = 0
    ZOMBIE = 1
    ZOMBIE_SPAWN = 2
    WALL = 3
    MY_BASE = 4
    MY_CAPITAL = 5
    ENEMY_BASE = 6
    ENEMY_CAPITAL = 7


class MapColors(str, enum.Enum):
    EMPTY = 'white'
    ZOMBIE = 'red'
    ZOMBIE_SPAWN = 'yellow'
    WALL = 'grey'
    MY_BASE = 'green'
    MY_CAPITAL = 'blue'
    ENEMY_BASE = 'orange'
    ENEMY_CAPITAL = 'purple'


# Функция для заполнения областей на карте
def fill_area(map_array, top_left, bottom_right, value):
    map_array[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]] = value


cmap = mpl_col.ListedColormap([color.value for color in MapColors])


def visualize_map(game_map: np.ndarray):
    x_size, y_size = game_map.shape

    plt.imshow(game_map, origin='lower', extent=(0, x_size, 0, y_size), vmin=0, vmax=len(cmap.colors), cmap=cmap)

    # Добавление сетки клеток
    plt.grid(which='both', color='black', linestyle='-', linewidth=1)

    # Настройка интервалов сетки с учетом смещения
    plt.xticks(np.arange(0, x_size, 1))
    plt.yticks(np.arange(0, y_size, 1))

    plt.grid(which='minor', color='black', linestyle='-', linewidth=1)

    # Убираем метки осей
    plt.tick_params(axis='both', which='both', length=0)
    plt.title("Game Map")
    plt.show()


def _main():
    grid_size = 20
    game_map = np.zeros((grid_size, grid_size))

    def fill_area(map_array, top_left, bottom_right, value):
        map_array[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]] = value

    # Заполняем карту объектами
    fill_area(game_map, (2, 2), (5, 5), MapNumbers.ZOMBIE.value)
    fill_area(game_map, (6, 6), (10, 10), MapNumbers.WALL.value)
    fill_area(game_map, (12, 2), (15, 5), MapNumbers.MY_BASE.value)
    game_map[13, 3] = MapNumbers.MY_CAPITAL.value
    fill_area(game_map, (2, 12), (5, 15), MapNumbers.ENEMY_BASE.value)
    game_map[3, 13] = MapNumbers.ENEMY_CAPITAL.value
    game_map[8, 8] = MapNumbers.ZOMBIE_SPAWN.value

    visualize_map(game_map)


if __name__ == '__main__':
    _main()

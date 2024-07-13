import datetime as dt
import logging
import logging.handlers
import time
import typing as tp
import sys

import client
import models
import utils
import store
import map_lib
import config
import visualize
from strategy import attacker
from strategy import builder
from strategy import base_mover

DTTM_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


start_time = dt.datetime.now()
logging.basicConfig(
    filename=f'logs/{start_time.strftime("%H-%M-%S")}.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    f'logs/{start_time.strftime("%H-%M-%S")}.log', maxBytes=(1048576*50000000), backupCount=1,
)
formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def get_nearest_round(game_client: client.Client) -> models.Round:
    response = game_client.get_rounds()
    now = utils.str_to_datetime(response['now'])
    rounds = [models.Round.from_record(record)
              for record in response['rounds']]

    nearest_round_delta = None
    nearest_round = None
    for round_ in rounds:
        ts_delta = abs((round_.start_at - now).total_seconds())
        # if ts_delta < 0:
        #     continue

        if nearest_round_delta is None or ts_delta < nearest_round_delta:
            nearest_round_delta = ts_delta
            nearest_round = round_

    if nearest_round is None:
        msg = 'No nearest round found'
        logger.error(msg)
        raise Exception(msg)

    return nearest_round


def send_participation(game_client: client.Client) -> int:
    response = game_client.put_participate()
    try:
        return response['startsInSec']
    except KeyError:
        if response['errCode'] == 1001:
            if 'you are participating in this realm' in response['error']:
                return 0
        msg = f'Error in participate {response}'
        logger.error(msg)
        raise Exception(msg)


def wait_till_next_turn(cur_turn: int, game_client: client.Client):
    response = game_client.get_units()
    turn: int = response['turn']
    turn_ends_in_ms: int = response['turnEndsInMs']

    while turn == cur_turn:
        time.sleep(turn_ends_in_ms / 1000 + 0.2)
        response = game_client.get_units()
        turn: int = response['turn']
        turn_ends_in_ms: int = response['turnEndsInMs']

    return response


def main():
    game_client = client.Client()

    next_round = get_nearest_round(game_client)

    logger.info(f'Preparing for round: {next_round.name} {next_round}')

    starts_in_sec = send_participation(game_client)

    logger.info(f'Registration complete! Next round starts in {starts_in_sec}')
    time.sleep(starts_in_sec)

    fresh_config = config.ConfigManager('configs/config_v1.json')

    # ROUND STARTS HERE

    logger.info('Got static world')
    game_store = store.Store(client=game_client)
    game_map = map_lib.Map(store=game_store, reserve_multiplier=fresh_config.get_config()[
        'map_reserve_multiplier'])

    cur_turn: int = -1

    while True:
        # Get next round info
        response = wait_till_next_turn(cur_turn, game_client)
        cur_turn = response['turn']
        logger.info(f'Starting round {cur_turn}')

        game_map.update()
        logger.info('Map updated')

        coins = game_map._info.gold
        turn = game_map._info.turn
        logger.info(f'Current turn: {turn}. Current coins: {coins}')

        # Strategy here
        attack = attacker.get_attack(game_map)
        build = builder.get_build(game_map)
        move_base = base_mover.get_move_base(game_map)
        logger.info('Strategy calculated')

        response = game_client.post_commands(attack, build, move_base)
        logger.info(f'Strategy sent for turn: {cur_turn}')

        # Visualization
        visualize.visualize_map(game_map=game_map.get_visible_map())
        logger.info('Visualizated')


if __name__ == '__main__':
    main()

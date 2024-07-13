import datetime as dt
import logging
import logging.handlers
import time
import typing as tp
import sys

import client
import models
import utils

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
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    f'logs/{start_time.strftime("%H-%M-%S")}.log', maxBytes=(1048576*5), backupCount=7,
)
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


def get_nearest_round(game_client: client.Client) -> models.Round:
    response = game_client.get_rounds()
    now = utils.str_to_datetime(response['now'])
    rounds = [models.Round.from_record(record) for record in response['rounds']]

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

    # ROUND STARTS HERE

    response = game_client.get_world()
    logger.info('Got static world')
    # TODO: init world map

    cur_turn: int = -1

    while True:
        # Get next round info
        response = wait_till_next_turn(cur_turn, game_client)
        cur_turn = response['turn']
        logger.info(f'Starting round {cur_turn}')

        # TODO: update world map
        ...
        logger.info('Map updated')

        # TODO: strategy here
        attack = ...
        build = ...
        move_base = ...
        logger.info('Strategy calculated')

        # response = game_client.post_commands(attack, build, move_base)
        logger.info('Strategy sent')


if __name__ == '__main__':
    main()

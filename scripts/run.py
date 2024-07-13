import datetime as dt
import logging
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
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
stdout_handler.setFormatter(stdout_formatter)
logger.addHandler(stdout_handler)


def get_nearest_round(game_client: client.Client) -> models.Round:
    response = game_client.get_rounds()
    now = utils.str_to_datetime(response['now'])
    rounds = [models.Round.from_record(record) for record in response['rounds']]

    nearest_round_delta = None
    nearest_round = None
    for round_ in rounds:
        ts_delta = (round_.start_at - now).total_seconds()
        if ts_delta < 0:
            continue

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


def main():
    game_client = client.Client()

    next_round = get_nearest_round(game_client)

    stats_in_sec = send_participation(game_client)

    logger.info('Next round starts in ')
    time.sleep(stats_in_sec)




if __name__ == '__main__':
    main()

import json
import time

import client


def log_request(result, op_type = ''):
    now_ts = int(time.time())
    print(result)

    with open(f'test_log/response_{op_type}_{now_ts}.json', 'w') as file:
        json.dump(result, file, indent=4)


def send_request(game_client: client.Client):

    # return game_client.put_participate()

    # return game_client.get_world()

    # return game_client.get_units()

    return game_client.get_rounds()


    return game_client.post_commands(attack, build, move_base)


def loop_fetch(game_client: client.Client):
    log_request(game_client.get_rounds(), 'get_rounds')

    log_request(game_client.put_participate(), 'put_participate')

    log_request(game_client.get_world(), 'get_world')

    while True:
        log_request(game_client.get_units(), 'get_units')
        time.sleep(2)


if __name__ == '__main__':
    game_client = client.Client()

    # loop_fetch(game_client)
    log_request(send_request(game_client))

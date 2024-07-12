import json

import client


def send_request(client: client.Client):

    # return client.put_participate()

    # return client.get_world()

    return client.get_units()

    # return client.get_rounds()


if __name__ == '__main__':
    game_client = client.Client()
    result = send_request(game_client)
    print(result)

    with open('response.json', 'w') as file:
        json.dump(result, file)

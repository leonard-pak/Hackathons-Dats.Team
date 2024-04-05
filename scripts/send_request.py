import client
from map import Universe
from ship import Ship


def send_request(client: client.Client):

    return Universe.create(client.get_universe()['universe'])
    # return client.get_universe()

    # planets = Universe.create(client.get_universe()).get_path("Earth", 'Mraz')
    # return client.post_travel(planets=planets)

    garbage = {}
    # return client.post_collect(garbage=garbage)

    # return client.delete_reset()

    # return Ship.create(client.get_universe()['ship'])

    return client.get_rounds()


if __name__ == '__main__':
    game_client = client.Client(2)
    for _ in range(10):
        result = send_request(game_client)
        print(result)

    # print(result.status_code)
    # print(result.text)

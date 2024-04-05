import client


def send_request(client: client.Client):

    return client.get_universe()

    # return client.post_travel(planets=)

    # return client.post_collect(garbage=)

    # return client.delete_reset()

    # return client.get_rounds()


if __name__ == '__main__':
    game_client = client.Client()
    result = send_request(game_client)
    print(result)
    print(result.status_code)
    print(result.text)

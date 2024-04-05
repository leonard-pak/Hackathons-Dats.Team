import dotenv
import logging
import os
import requests
import typing as tp


dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class Client():
    def __init__(self) -> None:
        self._host = os.getenv('HOST')
        self._token = os.getenv('TOKEN')
        self._auth_header = {'X-Auth-Token': self._token}

    def get_universe(self):
        uri = '/player/universe'
        url = self._host + uri
        return requests.get(url=url, headers=self._auth_header)

    def post_travel(self, planets: tp.List[str]):
        uri = '/player/travel'
        url = self._host + uri
        body = {
            'planets': planets,
        }
        return requests.post(url=url, json=body, headers=self._auth_header)

    def post_collect(self, garbage: tp.Dict[str, tp.List[tp.Tuple[int, int]]]):
        uri = '/player/collect'
        url = self._host + uri
        body = {
            'garbage': garbage,
        }
        return requests.post(url=url, json=body, headers=self._auth_header)

    def delete_reset(self):
        uri = '/player/reset'
        url = self._host + uri
        return requests.delete(url=url, headers=self._auth_header)

    def get_rounds(self):
        uri = '/player/rounds'
        url = self._host + uri
        return requests.get(url=url, headers=self._auth_header)

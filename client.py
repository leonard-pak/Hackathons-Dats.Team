import enum
import dotenv
import json
import logging
import os
import requests
import typing as tp
from time import time, sleep

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

class Method(enum.Enum):
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'

class Client():
    def __init__(self, period_call = 0.25) -> None:
        self._host = os.getenv('HOST')
        self._token = os.getenv('TOKEN')
        self._auth_header = {'X-Auth-Token': self._token}
        self._last_call = time()
        self._period_call = period_call

    def get_universe(self):
        uri = '/player/universe'
        url = self._host + uri
        response = self.__request(Method.GET, url=url)
        return json.loads(response.text)

    def post_travel(self, planets: tp.List[str]):
        uri = '/player/travel'
        url = self._host + uri
        body = {
            'planets': planets,
        }
        response = self.__request(Method.POST, url=url, json=body)
        return json.loads(response.text)

    def post_collect(self, garbage: tp.Dict[str, tp.List[tp.Tuple[int, int]]]):
        uri = '/player/collect'
        url = self._host + uri
        body = {
            'garbage': garbage,
        }
        response = self.__request(Method.POST, url=url, json=body)
        return json.loads(response.text)

    def delete_reset(self):
        uri = '/player/reset'
        url = self._host + uri
        response = self.__request(Method.DELETE, url=url)
        return json.loads(response.text)

    def get_rounds(self):
        uri = '/player/rounds'
        url = self._host + uri
        response = self.__request(Method.GET, url=url)
        return json.loads(response.text)

    def __request(self, method: Method, url: str, json = None):
        while (time() - self._last_call < self._period_call):
            sleep(self._period_call * 0.1)
        res = requests.request(method=method.value, url=url, headers=self._auth_header, json=json)
        self._last_call = time()
        return res

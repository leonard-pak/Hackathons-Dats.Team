import enum
import dotenv
import json
import logging
import os
import requests
import typing as tp
from time import time, sleep
import datetime as dt

from mock import collect_mock, universe_mock, travel_mock

dotenv.load_dotenv()
start_time = dt.datetime.now()
logger = logging.getLogger(__name__)
logger.basicConfig(
    filename=f'logs/{start_time.strftime("%H-%M-%S")}.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

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
        # return universe_mock
        uri = '/player/universe'
        url = self._host + uri
        response = self.__request(Method.GET, url=url)
        return json.loads(response.text)

    def post_travel(self, planets: tp.List[str]):
        # return travel_mock
        uri = '/player/travel'
        url = self._host + uri
        body = {
            'planets': planets,
        }
        response = self.__request(Method.POST, url=url, json=body)
        return json.loads(response.text)

    def post_collect(self, garbage: tp.Dict[str, tp.List[tp.Tuple[int, int]]]):
        # return collect_mock
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
        logger.debug(f'[{method.value}] [{url}] Payload: {json}')
        res = requests.request(method=method.value, url=url, headers=self._auth_header, json=json)
        logger.debug(f'[{method.value}] [{url}] Response: {res.text}')
        self._last_call = time()
        return res

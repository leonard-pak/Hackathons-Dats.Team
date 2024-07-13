import enum
import dotenv
import json
import logging
import os
import requests
import typing as tp
import time
import datetime as dt


import models


dotenv.load_dotenv()
start_time = dt.datetime.now()
logging.basicConfig(
    filename=f'logs/{start_time.strftime("%H-%M-%S")}.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class Method(enum.Enum):
    POST = 'POST'
    GET = 'GET'
    PUT = 'PUT'


class Client():
    def __init__(self, period_call = 0.25) -> None:
        host = os.getenv('HOST')
        if host is None:
            raise ValueError('Host not provided!')
        token = os.getenv('TOKEN')
        if token is None:
            raise ValueError('Token not provided!')
        self._host = host
        self._token = token
        self._auth_header = {'X-Auth-Token': self._token}
        self._last_call = time.time()
        self._period_call = period_call

    def _request(self, method: Method, url: str, payload = None):
        while (time.time() - self._last_call < self._period_call):
            time.sleep(self._period_call * 0.1)
        logger.debug(f'[{method.value}] [{url}] Payload: {payload}')
        res = requests.request(method=method.value, url=url, headers=self._auth_header, json=payload)
        logger.debug(f'[{method.value}] [{url}] Response: {res.text}')
        self._last_call = time.time()
        return res

    def post_commands(self, attack: tp.List[models.Attack], build: tp.List[models.Build], move_base: models.MoveBase):
        # return post_commands
        uri = '/play/zombidef/command'
        url = self._host + uri
        body = {
            'attack': attack,
            'build': build,
            'moveBase': move_base,
        }
        response = self._request(Method.POST, url=url, payload=body)
        return json.loads(response.text)

    def put_participate(self):
        # return post_commands
        uri = '/play/zombidef/participate'
        url = self._host + uri
        response = self._request(Method.PUT, url=url)
        return json.loads(response.text)

    def get_units(self):
        # return universe_mock
        uri = '/play/zombidef/units'
        url = self._host + uri
        response = self._request(Method.GET, url=url)
        return json.loads(response.text)

    def get_world(self):
        # return universe_mock
        uri = '/play/zombidef/world'
        url = self._host + uri
        response = self._request(Method.GET, url=url)
        return json.loads(response.text)

    def get_rounds(self):
        # return universe_mock
        uri = '/rounds/zombidef'
        url = self._host + uri
        response = self._request(Method.GET, url=url)
        return json.loads(response.text)

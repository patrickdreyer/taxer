from ...container import Container
from ..mergent import Mergent
from .coinbaseProApi import CoinbaseProApi
from .coinbaseProApiAuth import CoinbaseProApiAuth
from .coinbaseProApiReader import CoinbaseProApiReader


class CoinbaseProMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__container = container
        self.__config = config

    def createReaders(self):
        auth = CoinbaseProApiAuth(self.__config['key'], self.__config['secret'], self.__config['passphrase'])
        api = CoinbaseProApi(self.__config['url'], self.__config['symbols'], auth)
        yield CoinbaseProApiReader(self.__config['id'], api)

import ccxt

from ...container import Container
from ..mergent import Mergent
from .poloniexApiReader import PoloniexApiReader


class PoloniexMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__config = config

    def createReaders(self):
        api = ccxt.poloniex({
            'apiKey': self.__config['key'],
            'secret': self.__config['secret'],
        })
        yield PoloniexApiReader(self.__config['id'], api)

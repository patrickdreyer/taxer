import ccxt

from .poloniexApiReader import PoloniexApiReader
from ..mergent import Mergent


class PoloniexMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config

    def createReaders(self):
        api = ccxt.poloniex({
            'apiKey': self.__config['key'],
            'secret': self.__config['secret'],
        })
        yield PoloniexApiReader(self.__config['id'], api)

from ..mergent import Mergent
from .coinbaseProApi import CoinbaseProApi
from .coinbaseProApiAuth import CoinbaseProApiAuth
from .coinbaseProApiReader import CoinbaseProApiReader


class CoinbaseProMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config

    def createReaders(self):
        auth = CoinbaseProApiAuth(self.__config)
        api = CoinbaseProApi(self.__config, auth)
        yield CoinbaseProApiReader(self.__config, api)

from ..mergent import Mergent
from .coinbaseApiAuth import CoinbaseApiAuth
from .coinbaseCoinbaseAppApi import CoinbaseCoinbaseAppApi
from .coinbaseAdvancedTradeApi import CoinbaseAdvancedTradeApi
from .coinbaseApiReader import CoinbaseApiReader


class CoinbaseMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        if 'ETH' in self.__config['symbols']:
            self.__config['symbols'].append('ETH2')
        auth = CoinbaseApiAuth(self.__config['keyName'], self.__config['keySecret'])
        coinbaseAppApi = CoinbaseCoinbaseAppApi(self.__config['url'], self.__config['symbols'], auth)
        advancedTradeApi = CoinbaseAdvancedTradeApi(self.__config['symbols'], self.__config['keyName'], self.__config['keySecret'])
        yield CoinbaseApiReader(self.__config['id'], coinbaseAppApi, advancedTradeApi)

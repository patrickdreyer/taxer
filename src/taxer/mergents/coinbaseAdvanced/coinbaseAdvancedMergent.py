from ..mergent import Mergent
from .coinbaseAdvancedApi import CoinbaseAdvancedApi
from .coinbaseAdvancedApiAuth import CoinbaseAdvancedApiAuth
from .coinbaseAdvancedApiReader import CoinbaseAdvancedApiReader


class CoinbaseAdvancedMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        auth = CoinbaseAdvancedApiAuth(self.__config['apiKeyName'], self.__config['privateKey'])
        api = CoinbaseAdvancedApi(self.__config['url'], self.__config['symbols'], auth)
        yield CoinbaseAdvancedApiReader(self.__config['id'], api)

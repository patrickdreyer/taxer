import json
import requests

from ..currencyConverterApi import CurrencyConverterApi


class CoinGeckoApi(CurrencyConverterApi):
    def __init__(self, config):
        self.__config = config
        self.__session = requests.Session()

    def __del__(self):
        self.__session.close()

    def getSymbols(self):
        query = '{}/coins/list'.format(self.__config['apiUrl'])
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content

    def getRate(self, symbol, date):
        query = '{}/coins/{}/history?date={}&localization=false'.format(self.__config['apiUrl'], symbol, date.strftime('%d-%m-%Y'))
        response = self.__session.get(query)
        content = json.loads(response.content)
        return content['market_data']['current_price']['chf']

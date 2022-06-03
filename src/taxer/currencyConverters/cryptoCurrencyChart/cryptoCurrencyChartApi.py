import json
import requests


class CryptoCurrencyChartApi:
    def __init__(self, config):
        self.__config = config

    def getCoinList(self):
        query = 'https://{}:{}@{}/coin/list'.format(self.__config['apiKey'], self.__config['apiSecret'], self.__config['apiUrl'])
        with requests.Session() as session:
            response = session.get(query)
        content = json.loads(response.content)
        return content['coins']

    def getCoinMarketDataById(self, id, date):
        query = 'https://{}:{}@{}/coin/view/{}/{}/CHF'.format(self.__config['apiKey'], self.__config['apiSecret'], self.__config['apiUrl'], id, date.strftime('%Y-%m-%d'))
        with requests.Session() as session:
            response = session.get(query)
        content = json.loads(response.content)
        return content['coin']

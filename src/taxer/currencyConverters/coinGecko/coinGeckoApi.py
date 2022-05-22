import json
import requests


class CoinGeckoApi:
    def __init__(self, config):
        self.__config = config

    def getCoinList(self):
        with requests.Session() as session:
            response = session.get('{}/coins/list'.format(self.__config['apiUrl']))
        content = json.loads(response.content)
        return content

    def getCoinMarketDataById(self, id, date):
        query = '{}/coins/{}/history?date={}&localization=false'.format(self.__config['apiUrl'], id, date.strftime('%d-%m-%Y'))
        with requests.Session() as session:
            response = session.get(query)
        content = json.loads(response.content)
        return content['market_data']

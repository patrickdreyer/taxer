from collections import OrderedDict

from pycoingecko import CoinGeckoAPI


class CoinGeckoCurrencyConverter:
    __api = None
    __ids = dict()
    __cache = OrderedDict()

    def __init__(self):
        self.__api = CoinGeckoAPI()
        coins = self.__api.get_coins_list()
        for coin in coins:
            symbol = coin['symbol']
            id = coin['id']
            self.__ids[symbol.upper()] = id

    def exchangeRate(self, unit, date):
        cacheKey = '{0}{1}'.format(unit, date.strftime('%Y%m%d'))
        if cacheKey in self.__cache:
            return self.__cache[cacheKey]

        id = self.__ids[unit]
        response = self.__api.get_coin_history_by_id(id, date.strftime('%d-%m-%Y'))
        ret = response['market_data']['current_price']['chf']
        self.__cache[cacheKey] = ret
        return ret

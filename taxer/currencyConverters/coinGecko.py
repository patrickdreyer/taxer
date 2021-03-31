from pycoingecko import CoinGeckoAPI


class CoinGeckoCurrencyConverter:
    __api = None
    __ids = dict()

    def __init__(self):
        self.__api = CoinGeckoAPI()
        coins = self.__api.get_coins_list()
        for coin in coins:
            symbol = coin['symbol']
            id = coin['id']
            self.__ids[symbol.upper()] = id

    def exchangeRate(self, unit, date):
        id = self.__ids[unit]
        response = self.__api.get_coin_history_by_id(id, date.strftime('%d-%m-%Y'))
        ret = response['market_data']['current_price']['chf']
        return ret

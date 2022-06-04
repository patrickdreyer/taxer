import datetime
from  dateutil import parser
from decimal import Decimal
import hashlib
import hmac
import json
import requests

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.sellTrade import SellTrade


class CexApiReader(Reader):
    __symbols = [ 'BTC', 'ETH', 'XRP' ]

    def __init__(self, config):
        self.__config = config

    def read(self, year):
        orders = self.__fetchArchivedOrders(year)
        for order in orders:
            if not 'd' in order['status']:
                continue
            date = parser.isoparse(order['time'])
            fee = Currency(order['symbol2'], CexApiReader.__getAmount('fa', order))
            fiat = Currency(order['symbol2'], CexApiReader.__getAmount('ta', order))
            remains = Currency(order['symbol1'], order['remains'])
            crypto = Currency(order['symbol1'], order['a:{}:cds'.format(order['symbol1'])]) - remains
            if order['type'] == 'sell':
                fiat = fiat - fee
                yield SellTrade(self.__config['id'], date, order['id'], crypto, fiat, fee)
            elif order['type'] == 'buy':
                yield BuyTrade(self.__config['id'], date, order['id'], crypto, fiat, fee)

    def __fetchArchivedOrders(self, year):
        for symbol in self.__symbols:
            request = {
                'dateTo': datetime.datetime(year, 12, 31).timestamp(),
                'dateFrom': datetime.datetime(year, 1, 1).timestamp(),
                'lastTxDateTo': datetime.datetime(year, 12, 31).timestamp(),
                'lastTxDateFrom': datetime.datetime(year, 1, 1).timestamp()
            }
            add = self.__createSignature()
            request.update(add)
            response = requests.post('{}/archived_orders/{}/USD'.format(self.__config['apiUrl'], symbol),
                json = request,
                headers = {'content-type': 'application/json'})
            yield from json.loads(response.content)

    def __createSignature(self):
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        message = "{}{}{}".format(timestamp, self.__config['userId'], self.__config['key'])
        signature = hmac.new(self.__config['secret'].encode(), message.encode(), hashlib.sha256).hexdigest()
        return {
            'key': self.__config['key'],
            'signature': signature,
            'nonce': timestamp,
        }

    @staticmethod
    def __getAmount(id, order):
        maker = '{}:{}'.format(id, order['symbol2'])
        taker = 't{}:{}'.format(id, order['symbol2'])
        ret = Decimal()
        if maker in order:
            ret = ret + Decimal(order[maker])
        if taker in order:
            ret = ret + Decimal(order[taker])
        return ret

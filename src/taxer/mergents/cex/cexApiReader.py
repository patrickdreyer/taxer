from datetime import datetime
from dateutil import parser
from decimal import Decimal
import hashlib
import hmac
import json
from pytz import utc
import requests

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.sellTrade import SellTrade


class CexApiReader(Reader):
    __symbols = [ 'BTC', 'ETH', 'XRP' ]

    def __init__(self, id:str, url:str, userId:str, key:str, secret:str):
        self.__id = id
        self.__url = url
        self.__userId = userId
        self.__key = key
        self.__secret = secret.encode()

    def read(self, year):
        orders = self.__fetchArchivedOrders(year)
        for order in orders:
            if not 'd' in order['status']:
                continue
            date = parser.isoparse(order['time'])
            fee = Currency(order['symbol2'], CexApiReader.__getAmount('fa', order))
            fiat = Currency(order['symbol2'], CexApiReader.__getAmount('ta', order))
            crypto = Currency(order['symbol1'], order['a:{}:cds'.format(order['symbol1'])])
            if order['type'] == 'sell':
                fiat = fiat - fee
                yield SellTrade(self.__id, date, order['id'], crypto, fiat, fee)
            elif order['type'] == 'buy':
                yield BuyTrade(self.__id, date, order['id'], crypto, fiat, fee)

    def __fetchArchivedOrders(self, year):
        start = datetime(year, 1, 1, tzinfo=utc).timestamp()
        end = datetime(year, 12, 31, tzinfo=utc).timestamp()
        for symbol in self.__symbols:
            request = {
                'dateFrom': start,
                'dateTo': end,
                'lastTxDateFrom': start,
                'lastTxDateTo': end
            }
            add = self.__createSignature()
            request.update(add)
            response = requests.post('{}/archived_orders/{}/USD'.format(self.__url, symbol),
                json = request,
                headers = {'content-type': 'application/json'})
            yield from json.loads(response.content)

    def __createSignature(self):
        timestamp = int(datetime.now(utc).timestamp() * 1000)
        message = "{}{}{}".format(timestamp, self.__userId, self.__key)
        signature = hmac.new(self.__secret, message.encode(), hashlib.sha256).hexdigest()
        return {
            'key': self.__key,
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

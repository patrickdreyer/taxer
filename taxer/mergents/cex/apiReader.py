import datetime
from  dateutil import parser
import hashlib
import hmac
import json
import requests

from ..reader import Reader
from ...transactions.currency import Currency
from ...transactions.sellTrade import SellTrade
from ...transactions.buyTrade import BuyTrade


class CexApiReader(Reader):
    def __init__(self, config):
        self.__config = config

    def read(self, year):
        orders = self.__fetchArchivedOrders(year)
        for order in orders:
            if not 'd' in order['status']:
                continue
            date = parser.isoparse(order['time'])
            crypto = Currency(order['symbol1'], order['a:{}:cds'.format(order['symbol1'])])
            fee = Currency(order['symbol2'], order['f:{}:cds'.format(order['symbol2'])])
            fiat = Currency(order['symbol2'], order['a:{}:cds'.format(order['symbol2'])]) - fee
            if order['type'] == 'sell':
                yield SellTrade('CEX', date, order['id'], crypto, fiat, fee)
            elif order['type'] == 'buy':
                yield BuyTrade('CEX', date, order['id'], crypto, fiat, fee)

    def __fetchArchivedOrders(self, year):
        for symbol in self.__config['symbols']:
            request = {
                "dateTo": datetime.datetime(year, 12, 31).timestamp(),
                "dateFrom": datetime.datetime(year, 1, 1).timestamp(),
                "lastTxDateTo": datetime.datetime(year, 12, 31).timestamp(),
                "lastTxDateFrom": datetime.datetime(year, 1, 1).timestamp()
            }
            add = self.__createSignature()
            request.update(add)
            response = requests.post('https://cex.io/api/archived_orders/{}/USD'.format(symbol),
                json = request,
                headers = {'content-type': 'application/json'})
            yield from json.loads(response.content)

    def __createSignature(self):
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        message = "{}{}{}".format(timestamp, self.__config['userId'], self.__config['key'])
        signature = hmac.new(self.__config['secret'].encode(), message.encode(), hashlib.sha256).hexdigest()
        return {
            "key": self.__config['key'],
            "signature": signature,
            "nonce": timestamp,
        }

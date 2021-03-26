import csv

from ..reader import Reader
from ..buyTrade import BuyTrade
from ..sellTrade import SellTrade


class CoinbaseProReader(Reader):
    __path = None

    def __init__(self, path=None):
        self.__path = path

    def read(self):
        with open(self.__path) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                if row['product'] != None:
                    if row['side'] == 'BUY':
                        yield BuyTrade('CBP', row['created at'], row['trade id'], row['size unit'], float(row['size']), row['price/fee/total unit'], abs(float(row['total']))-float(row['fee']), float(row['fee']))
                    if row['side'] == 'SELL':
                        yield SellTrade('CBP', row['created at'], row['trade id'], row['price/fee/total unit'], abs(float(row['total']))-float(row['fee']), row['size unit'], row['size'], float(row['fee']))

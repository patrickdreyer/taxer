import csv
from  dateutil import parser

from ..reader import Reader
from ..buyTrade import BuyTrade
from ..sellTrade import SellTrade
from ..withdrawTransfer import WithdrawTransfer
from ..depositTransfer import DepositTransfer


class CoinbaseProReader(Reader):
    def __init__(self, path):
        self.__path = path

    def read(self):
        with open(self.__path) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                # fills
                if 'product' in row:
                    if row['side'] == 'BUY':
                        yield BuyTrade('CBP', parser.isoparse(row['created at']), row['trade id'], row['size unit'], float(row['size']), row['price/fee/total unit'], abs(float(row['total']))-float(row['fee']), float(row['fee']))
                    elif row['side'] == 'SELL':
                        yield SellTrade('CBP', parser.isoparse(row['created at']), row['trade id'], row['size unit'], float(row['size']), row['price/fee/total unit'], abs(float(row['total']))-float(row['fee']), float(row['fee']))
                # accounts
                elif 'type' in row:
                    if row['type'] == 'withdrawal':
                        yield WithdrawTransfer('CBP', parser.isoparse(row['time']), row['transfer id'], row['amount/balance unit'], float(row['amount']))
                    elif row['type'] == 'deposit':
                        yield DepositTransfer('CBP', parser.isoparse(row['time']), row['transfer id'], row['amount/balance unit'], float(row['amount']))

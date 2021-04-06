import csv
from  dateutil import parser

from ..fileReader import FileReader
from ...transactions.buyTrade import BuyTrade
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class CoinbaseProFileReader(FileReader):
    __fileNamePattern = r'.*CoinbasePro.*\.csv'

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return CoinbaseProFileReader.__fileNamePattern

    def readFile(self, filePath):
        rows = self.__readFile(filePath)
        for row in rows:
            # fills
            if 'product' in row:
                if row['side'] == 'BUY':
                    yield BuyTrade('CBP', parser.isoparse(row['created at']), row['trade id'], row['size unit'], float(row['size']), row['price/fee/total unit'], abs(float(row['total']))-float(row['fee']), float(row['fee']))
                elif row['side'] == 'SELL':
                    yield SellTrade('CBP', parser.isoparse(row['created at']), row['trade id'], row['size unit'], float(row['size']), row['price/fee/total unit'], float(row['total'])-float(row['fee']), float(row['fee']))
            # accounts
            elif 'type' in row:
                if row['type'] == 'withdrawal':
                    yield WithdrawTransfer('CBP', parser.isoparse(row['time']), row['transfer id'], row['amount/balance unit'], abs(float(row['amount'])), 0)
                elif row['type'] == 'deposit':
                    yield DepositTransfer('CBP', parser.isoparse(row['time']), row['transfer id'], row['amount/balance unit'], float(row['amount']))

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

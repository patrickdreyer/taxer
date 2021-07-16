import csv
from logging import currentframe
from  dateutil import parser

from ..fileReader import FileReader
from ...transactions.currency import Currency
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

    def readFile(self, filePath, year):
        rows = self.__readFile(filePath)
        for row in rows:
            # fills
            if 'product' in row:
                date = parser.isoparse(row['created at'])
                if date.year != year:
                    continue
                crypto = Currency(row['size unit'], row['size'])
                fiatTotal = Currency(row['price/fee/total unit'], row['total'])
                fee = Currency(row['price/fee/total unit'], row['fee'])
                fiatAmount = fiatTotal - fee
                if row['side'] == 'BUY':
                    yield BuyTrade('CBP', date, row['trade id'], crypto, fiatAmount, fee)
                elif row['side'] == 'SELL':
                    yield SellTrade('CBP', date, row['trade id'], crypto, fiatAmount, fee)
            # accounts
            elif 'type' in row:
                date = parser.isoparse(row['time'])
                if date.year != year:
                    continue
                amount = Currency(row['amount/balance unit'], row['amount'])
                f = Currency(row['amount/balance unit'], 0)
                if row['type'] == 'withdrawal':
                    yield WithdrawTransfer('CBP', date, row['transfer id'], amount, f)
                elif row['type'] == 'deposit':
                    yield DepositTransfer('CBP', date, row['transfer id'], amount, f)

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

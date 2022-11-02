import csv
from  dateutil import parser
from pytz import utc

from ..fileReader import FileReader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer


class CoinbaseProFileReader(FileReader):
    def __init__(self, config, path):
        super().__init__(path)
        self.__config = config

    @property
    def filePattern(self):
        return self.__config['fileNamePattern']

    def readFile(self, filePath, year):
        rows = self.__readFile(filePath)
        for row in rows:
            # fills
            if 'product' in row:
                date = utc.localize(parser.isoparse(row['created at']))
                if date.year != year:
                    continue
                crypto = Currency(row['size unit'], row['size'])
                fiat = Currency(row['price/fee/total unit'], row['total'])
                fee = Currency(row['price/fee/total unit'], row['fee'])
                if row['side'] == 'BUY':
                    test = fiat.amount - fee.amount
                    fiat = fiat - fee
                    yield BuyTrade(self.__config['id'], date, row['trade id'], crypto, fiat, fee)
                elif row['side'] == 'SELL':
                    yield SellTrade(self.__config['id'], date, row['trade id'], crypto, fiat, fee)
            # accounts
            elif 'type' in row:
                date = parser.isoparse(row['time'])
                if date.year != year:
                    continue
                amount = Currency(row['amount/balance unit'], row['amount'])
                f = Currency(row['amount/balance unit'], 0)
                if row['type'] == 'withdrawal':
                    yield WithdrawTransfer(self.__config['id'], date, row['transfer id'], amount, f)
                elif row['type'] == 'deposit':
                    yield DepositTransfer(self.__config['id'], date, row['transfer id'], amount, f)

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

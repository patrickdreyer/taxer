import csv
import re
from  dateutil import parser

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class BitBoxReader(Reader):
    __satoshiToBTC = 0.00000001

    def __init__(self, path=None):
        self.__path = path

    def read(self):
        self.__rows = self.readFile()
        for self.__row in self.__rows:
            id = self.__row['Transaction ID']
            date = parser.isoparse(self.__row['Time'])
            unit = self.__row['Unit']
            amount = float(self.__row['Amount'])
            if unit == 'satoshi':
                unit = 'BTC'
                amount = amount * BitBoxReader.__satoshiToBTC

            if self.__row['Type'] == 'sent':
                feeAmount = float(self.__row['Fee'])
                if self.__row['Unit'] == 'satoshi':
                    feeAmount = feeAmount * BitBoxReader.__satoshiToBTC
                yield WithdrawTransfer('BB2', date, id, unit, amount, feeAmount)

            elif self.__row['Type'] == 'received':                        
                yield DepositTransfer('BB2', date, id, unit, amount)

    def readFile(self):
        with open(self.__path) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

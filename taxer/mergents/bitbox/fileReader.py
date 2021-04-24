import csv
from  dateutil import parser

from ..fileReader import FileReader
from ...transactions.buyTrade import BuyTrade
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class BitBoxFileReader(FileReader):
    __id = 'S'
    __fileNamePattern = r'BitBox.*\.csv'
    __satoshiToBTC = 0.00000001

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return BitBoxFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        self.__rows = self.__readFile(filePath)
        for self.__row in self.__rows:
            date = parser.isoparse(self.__row['Time'])
            if date.year != year:
                continue

            id = self.__row['Transaction ID']
            unit = self.__row['Unit']
            amount = float(self.__row['Amount'])
            if unit == 'satoshi':
                unit = 'BTC'
                amount = amount * BitBoxFileReader.__satoshiToBTC

            if self.__row['Type'] == 'sent':
                feeAmount = float(self.__row['Fee'])
                if self.__row['Unit'] == 'satoshi':
                    feeAmount = feeAmount * BitBoxFileReader.__satoshiToBTC
                yield WithdrawTransfer(BitBoxFileReader.__id, date, id, unit, amount-feeAmount, feeAmount)

            elif self.__row['Type'] == 'received':                        
                yield DepositTransfer(BitBoxFileReader.__id, date, id, unit, amount)

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

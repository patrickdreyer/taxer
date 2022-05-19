import csv
from  dateutil import parser

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class BitBoxFileReader(FileReader):
    __id = 'S'
    __fileNamePattern = r'BitBox.*\.csv'

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
            c = Currency(self.__row['Unit'], self.__row['Amount'])

            if self.__row['Type'] == 'sent':
                f = Currency(self.__row['Unit'], self.__row['Fee'])
                yield WithdrawTransfer(BitBoxFileReader.__id, date, id, c, f, self.__row['Note'])

            elif self.__row['Type'] == 'received':
                yield DepositTransfer(BitBoxFileReader.__id, date, id, c, Currency(self.__row['Unit'], 0), self.__row['Note'])

    def __readFile(self, filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

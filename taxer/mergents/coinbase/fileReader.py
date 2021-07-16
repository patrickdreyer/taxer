import csv
from  dateutil import parser

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class CoinbaseFileReader(FileReader):
    __id = 'CB'
    __fileNamePattern = r'.*Coinbase(?!Pro).*\.csv'

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return CoinbaseFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        rows = CoinbaseFileReader.__readFile(filePath)
        CoinbaseFileReader.__skipHeader(rows)
        for row in rows:
            date = parser.isoparse(row[0])
            if date.year != year:
                continue
            amount = Currency(row[2], row[3])
            f = Currency(row[2], 0)
            if row[1] == 'Send':
                yield WithdrawTransfer(CoinbaseFileReader.__id, date, '', amount, f)
            elif row[1] == 'Receive':
                yield DepositTransfer(CoinbaseFileReader.__id, date, '', amount, f)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            yield from reader

    @staticmethod
    def __skipHeader(rows):
        while True:
            header = next(rows)
            if len(header) == 0:
                continue
            if header[0] == 'Timestamp':
                return

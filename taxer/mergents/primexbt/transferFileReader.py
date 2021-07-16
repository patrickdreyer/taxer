import csv
from  dateutil import parser
import pytz

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class PrimeXBTTransferFileReader(FileReader):
    __fileNamePattern = r'.*primexbt.*transfer.*\.csv'

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return PrimeXBTTransferFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        self.__year = year
        rows = self.__readFile(filePath)
        for row in rows:
            date = pytz.utc.localize(parser.parse(row['Date/Time '].replace('\n', 'T')))
            if date.year != self.__year:
                continue
            symbol = row['Amount '].split()[1]
            amount = Currency(symbol, row['Amount '].split()[0])
            f = Currency(symbol, 0)
            if row['From '].find('Blockchain') != -1:
                yield DepositTransfer('PRM', date, row['ID '], amount, f)
            elif row['To '].find('Blockchain') != -1:
                yield WithdrawTransfer('PRM', date, row['ID '], amount, f)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

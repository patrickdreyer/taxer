import csv
from  dateutil import parser
import pytz

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class PrimeXBTTransferFileReader(FileReader):
    def __init__(self, config, path):
        super().__init__(path)
        self.__config = config

    @property
    def filePattern(self):
        return self.__config['fileNamePatterns']['transfer']

    def readFile(self, filePath, year):
        self.__year = year
        rows = self.__readFile(filePath)
        for row in rows:
            date = pytz.utc.localize(parser.parse(row['Date/Time']))
            if date.year != self.__year:
                continue
            symbol = row['Amount'].split()[1]
            amount = Currency(symbol, row['Amount'].split()[0])
            f = Currency(symbol, 0)
            if row['From'].find('Blockchain') != -1:
                yield DepositTransfer(self.__config['id'], date, row['ID'], amount, f)
            elif row['To'].find('Blockchain') != -1:
                yield WithdrawTransfer(self.__config['id'], date, row['ID'], amount, f)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

import csv
from dateutil import parser
import re
from pytz import utc

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class RowParserFactory:
    @staticmethod
    def create(row):
        return RowParser2020(row) if 'Date/Time ' in row else RowParser(row)

class RowParser:
    def __init__(self, row):
        self._row = row
    def __call__(self, row):
        self._row = row
        return self
    @property
    def dateTime(self):
        return self._row['Date/Time']
    @property
    def id(self):
        return self._row['ID']
    @property
    def amount(self):
        return self._row['Amount']
    @property
    def frm(self):
        return self._row['From']
    @property
    def to(self):
        return self._row['To']
    @property
    def info(self):
        return self._row['Info']

class RowParser2020(RowParser):
    @property
    def dateTime(self):
        return self._row['Date/Time '].replace('\n', 'T')
    @property
    def id(self):
        return self._row['ID ']
    @property
    def amount(self):
        return self._row['Amount ']
    @property
    def frm(self):
        return self._row['From ']
    @property
    def to(self):
        return self._row['To ']
    @property
    def info(self):
        return self._row['Info ']


class PrimeXBTTransferFileReader(FileReader):
    def __init__(self, config, path):
        super().__init__(path)
        self.__config = config
        self.__infoPattern = re.compile(r'address (.*)$') # 'Blockchain withdrawal: e55d9cf348daaee9983305d368cf11268ff7a9b22062a56de791e6b6c7b19bc4, address 37Dm4VhGAyCbfpVXuh837K2yNXEaAUg2Zs'

    @property
    def filePattern(self):
        return self.__config['fileNamePatterns']['transfer']

    def readFile(self, filePath, year):
        rowParser = None
        self.__year = year
        rows = self.__readFile(filePath)
        for row in rows:
            rowParser = rowParser(row) if rowParser else RowParserFactory.create(row)
            date = utc.localize(parser.parse(rowParser.dateTime))
            if date.year != self.__year:
                continue
            symbol = rowParser.amount.split()[1]
            amount = Currency(symbol, rowParser.amount.split()[0])
            f = Currency(symbol, 0)
            address = self.__infoPattern.search(rowParser.info).group(1)
            if rowParser.frm.find('Blockchain') != -1:
                yield DepositTransfer(self.__config['id'], date, rowParser.id, amount, f, address)
            elif rowParser.to.find('Blockchain') != -1:
                yield WithdrawTransfer(self.__config['id'], date, rowParser.id, amount, f, address)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

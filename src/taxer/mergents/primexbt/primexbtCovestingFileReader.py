import csv
import datetime
from  dateutil import parser
from decimal import Decimal
import pytz

from ..fileReader import FileReader
from ...transactions.covesting import Covesting
from ...transactions.currency import Currency


class PrimeXBTCovestingFileReader(FileReader):
    __startEntryFee = pytz.utc.localize(datetime.datetime(2020, 12, 1))
    __entryFeePercentage = Decimal(0.01)

    def __init__(self, config, path):
        super().__init__(path)
        self.__config = config

    @property
    def filePattern(self):
        return self.__config['fileNamePatterns']['covesting']

    def readFile(self, filePath, year):
        self.__year = year
        rows = self.__readFile(filePath)
        for row in rows:
            date = pytz.utc.localize(parser.parse(row['Closing date']))
            if date.year != self.__year:
                continue
            symbol = row['Total profit'].split()[1]
            amount = Currency(symbol, row['Total profit'].split()[0])
            entryFee = Currency(symbol, Decimal(row['Initial equity'].split()[0]) * PrimeXBTCovestingFileReader.__entryFeePercentage if date >= PrimeXBTCovestingFileReader.__startEntryFee else 0)
            exitFee = Currency(symbol, row['Commission'].split()[0])
            yield Covesting(self.__config['id'], date, '', row['Name'], amount, entryFee, exitFee)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

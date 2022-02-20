import csv
from dateutil import parser
from dateutil.parser import parserinfo
from decimal import Decimal
import os
import re

from .currencyConverter import CurrencyConverter


class ParserInfoDE(parserinfo):
    MONTHS = ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']


# https://excelrates.com/historical-exchange-rates/FROM-TO
class ExcelRates(CurrencyConverter):
    __parserInfo = ParserInfoDE()
    __rates = dict()

    def load(self, cachePath):
        fileMatches = self.__getFileMatches(cachePath)
        for unit, filePath in fileMatches:
            self.__load(unit, filePath)

    def store(self, cachePath):
        pass

    def exchangeRate(self, unit, date):
        rates = self.__rates[unit]
        rate = rates[date.strftime('%Y%m%d')]
        return rate

    def __getFileMatches(self, cachePath):
        for dirPath, _, fileNames in os.walk(cachePath):
            for fileName in fileNames:
                match = re.match(r'Excelrates_(.*)\.csv', fileName, flags=re.IGNORECASE)
                if match:
                    yield (match.group(1), os.path.join(dirPath, fileName))

    def __load(self, unit, filePath):
        unitRates = {}
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                d = parser.parse(row['Date'], ExcelRates.__parserInfo).strftime('%Y%m%d')
                unitRates[d] = Decimal(row['CHF'])
        ExcelRates.__rates[unit] = unitRates
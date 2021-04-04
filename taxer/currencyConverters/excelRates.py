import os
import re
import csv
import dateutil

from .currencyConverter import CurrencyConverter


class ParserInfoDE(dateutil.parser.parserinfo):
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
        # if not unit in self.__rates:
        #     unitRates = {}
        #     filePath = os.path.join(self.__path, 'Excelrates_{0}.csv'.format(unit))
        #     with open(filePath) as csvFile:
        #         reader = csv.DictReader(csvFile, delimiter=',')
        #         for row in reader:
        #             d = dateutil.parser.parse(row['Date'], self.__parserInfo).strftime('%Y%m%d')
        #             unitRates[d] = float(row['CHF'])
        #     self.__rates[unit] = unitRates
        unitRates = self.__rates[unit]
        unitRate = unitRates[date.strftime('%Y%m%d')]
        return unitRate

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
                d = dateutil.parser.parse(row['Date'], self.__parserInfo).strftime('%Y%m%d')
                unitRates[d] = float(row['CHF'])
        self.__rates[unit] = unitRates

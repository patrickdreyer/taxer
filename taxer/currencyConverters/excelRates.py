import os
import re
import csv
import dateutil


class ParserInfoDE(dateutil.parser.parserinfo):
    MONTHS = ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']


# https://excelrates.com/historical-exchange-rates/FROM-TO
class ExcelRates:
    __parserInfo = ParserInfoDE()
    __rates = {}
    __path = None

    def __init__(self, path):
        self.__path = path

    def exchangeRate(self, unit, date):
        if not unit in self.__rates:
            unitRates = {}
            filePath = os.path.join(self.__path, 'Excelrates_{0}.csv'.format(unit))
            with open(filePath) as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    d = dateutil.parser.parse(row['Date'], self.__parserInfo).strftime('%Y%m%d')
                    unitRates[d] = float(row['CHF'])
            self.__rates[unit] = unitRates
        unitRates = self.__rates[unit]
        unitRate = unitRates[date.strftime('%Y%m%d')]
        return unitRate

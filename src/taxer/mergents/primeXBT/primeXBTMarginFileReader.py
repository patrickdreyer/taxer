import csv
from  dateutil import parser
import itertools
from pytz import utc

from ..fileReader import FileReader
from ...transactions.currency import Currency
from ...transactions.marginTrade import MarginTrade


class PrimeXBTMarginFileReader(FileReader):
    def __init__(self, config, path):
        super().__init__(path)
        self.__config = config

    @property
    def filePattern(self):
        return self.__config['fileNamePatterns']['margin']

    def readFile(self, filePath, year):
        self.__year = year
        rows = PrimeXBTMarginFileReader.__readFile(filePath)
        next(rows)
        positions = filter(PrimeXBTMarginFileReader.__keepPositions, rows)
        convertedPositions = map(PrimeXBTMarginFileReader.__convertRow, positions)
        filteredYear = filter(self.__filterWrongYear, convertedPositions)
        sortedByPositionId = sorted(filteredYear, key=lambda r:r[0])
        groupedByPositionId = itertools.groupby(sortedByPositionId, key=lambda r:r[0])
        for positionId, positionGroup in groupedByPositionId:
            sortedPositionGroup = sorted(positionGroup, key=lambda r:r[3])
            symbol = sortedPositionGroup[0][6].split('/')[0]
            amount = Currency(symbol, sortedPositionGroup[2][9])
            entryFee = Currency(symbol, sortedPositionGroup[0][9])
            exitFee = Currency(symbol, sortedPositionGroup[1][9])
            yield MarginTrade(self.__config['id'], sortedPositionGroup[0][3], positionId, amount, entryFee, exitFee)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            yield from reader

    @staticmethod
    def __keepPositions(row):
        return True if row[0] != '' else False    

    @staticmethod
    def __convertRow(row):
        row[3] = utc.localize(parser.parse(row[3]))
        return row

    def __filterWrongYear(self, row):
        return row[3].year == self.__year

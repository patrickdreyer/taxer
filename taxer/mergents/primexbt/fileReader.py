import csv
import datetime
import itertools
import re
from  dateutil import parser
import pytz

from ..fileReader import FileReader
from ...transactions.covesting import Covesting
from ...transactions.currency import Currency
from ...transactions.marginTrade import MarginTrade
from ...transactions.withdrawTransfer import WithdrawTransfer
from ...transactions.depositTransfer import DepositTransfer


class PrimeXBTFileReader(FileReader):
    __fileNamePattern = r'.*primexbt.*\.csv'
    __startEntryFee = pytz.utc.localize(datetime.datetime(2020, 12, 1))
    __entryFeePercentage = 0.01

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return PrimeXBTFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        self.__year = year
        self.__canceled = list()
        rows = PrimeXBTFileReader.__readFile(filePath)
        header = next(rows)
        if header[0] == 'Name':
            yield from self.__readCovesting(rows)
        elif header[0] == 'Position ID':
            yield from self.__readMargin(rows)
        elif header[0] == 'Date/Time':
            yield from self.__readTransfers(rows)

    def __readCovesting(self, rows):
        for row in rows:
            date = pytz.utc.localize(parser.parse(row[4]))
            if date.year != self.__year:
                continue
            symbol = row[1].split()[1]
            amount = Currency(symbol, row[1].split()[0])
            entryFee = Currency(symbol, float(row[5].split()[0]) * PrimeXBTFileReader.__entryFeePercentage if date >= PrimeXBTFileReader.__startEntryFee else 0)
            exitFee = Currency(symbol, row[7].split()[0])
            yield Covesting('PRM', date, '', row[0], amount, entryFee, exitFee)

    def __readMargin(self, rows):
        positions = filter(PrimeXBTFileReader.__keepPositions, rows)
        convertedPositions = map(PrimeXBTFileReader.__convertRow, positions)
        filteredYear = filter(self.__filterWrongYear, convertedPositions)
        sortedByPositionId = sorted(filteredYear, key=lambda r:r[0])
        groupedByPositionId = itertools.groupby(sortedByPositionId, key=lambda r:r[0])
        for positionId, positionGroup in groupedByPositionId:
            sortedPositionGroup = sorted(positionGroup, key=lambda r:r[3])
            symbol = sortedPositionGroup[0][6].split('/')[0]
            amount = Currency(symbol, sortedPositionGroup[2][9])
            entryFee = Currency(symbol, sortedPositionGroup[0][9])
            exitFee = Currency(symbol, sortedPositionGroup[1][9])
            yield MarginTrade('PRM', sortedPositionGroup[0][3], positionId, amount, entryFee, exitFee)

    def __readTransfers(self, rows):
        for row in rows:
            date = pytz.utc.localize(parser.parse(row[0].replace('\n', 'T')))
            if date.year != self.__year:
                continue
            symbol = row[3].split()[1]
            amount = Currency(symbol, row[3].split()[0])
            if row[2].find('Deposit') != -1:
                yield DepositTransfer('PRM', date, row[1], amount)
            elif row[2].find('Withdrawal') != -1:
                yield WithdrawTransfer('PRM', date, row[1], amount, Currency(symbol, 0))

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
        row[3] = pytz.utc.localize(parser.parse(row[3]))
        return row

    def __filterWrongYear(self, row):
        return row[3].year == self.__year

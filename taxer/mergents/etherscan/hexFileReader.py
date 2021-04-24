import csv
import datetime
import itertools
import re
from  dateutil import parser

from ..fileReader import FileReader


class HEXFileReader(FileReader):
    __fileNamePattern = r'.*hex.*\.csv'
    __startDate = datetime.date(2019, 12, 2)

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return HEXFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        rows = HEXFileReader.__readFile(filePath)
        return map(HEXFileReader.__convertRow, rows)

    @staticmethod
    def __readFile(filePath):
        with open(filePath) as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            yield from reader

    @staticmethod
    def __convertRow(row):
        ret = {
            'date': HEXFileReader.__startDate + datetime.timedelta(days=int(row['Day'])),
            'HEX' : float(row['Your HEX'].replace(',', '')),
            'ETH' : float(row['Your ETH'])
        }
        return ret

import csv

from ..mergent import Mergent
from .fileReader import CoinbaseFileReader


class CoinbaseMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield CoinbaseFileReader(inputPath)

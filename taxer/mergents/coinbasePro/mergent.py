import csv

from ..mergent import Mergent
from .fileReader import CoinbaseProFileReader


class CoinbaseProMergent(Mergent):
    def createReaders(self, path):
        yield CoinbaseProFileReader(path)

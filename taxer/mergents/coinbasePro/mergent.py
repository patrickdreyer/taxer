import csv

from ..mergent import Mergent
from .fileReader import CoinbaseProFileReader


class CoinbaseProMergent(Mergent):
    def createReaders(self, config, path):
        yield CoinbaseProFileReader(path)

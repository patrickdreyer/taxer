import csv

from ..mergent import Mergent
from .reader import CoinbaseProReader


class CoinbaseProMergent(Mergent):
    @property
    def filePattern(self):
        return r'.*CoinbasePro.*\.csv'

    def createReader(self, path):
        return CoinbaseProReader(path)

import csv

from ..mergent import Mergent
from .reader import BitBoxReader


class BitBoxMergent(Mergent):
    @property
    def filePattern(self):
        return r'BitBox.*\.csv'

    def createReader(self, path):
        return BitBoxReader(path)

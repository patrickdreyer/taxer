import csv

from ..mergent import Mergent
from .reader import CexReader


class CexMergent(Mergent):
    @property
    def filePattern(self):
        return r'.*CEX.*\.csv'

    def createReader(self, path):
        return CexReader(path)

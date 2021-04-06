import csv

from ..mergent import Mergent
from .fileReader import CexFileReader


class CexMergent(Mergent):
    def createReaders(self, path):
        yield CexFileReader(path)

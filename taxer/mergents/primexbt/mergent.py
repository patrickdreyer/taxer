import csv

from ..mergent import Mergent
from .fileReader import PrimeXBTFileReader


class PrimeXBTMergent(Mergent):
    def createReaders(self, config, path):
        yield PrimeXBTFileReader(path)

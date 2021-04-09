import csv

from ..mergent import Mergent
from .fileReader import CexFileReader
from .apiReader import CexApiReader


class CexMergent(Mergent):
    def createReaders(self, config, path):
        yield CexFileReader(path)
        yield CexApiReader(config['cex'])

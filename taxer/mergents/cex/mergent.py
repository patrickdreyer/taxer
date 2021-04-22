import csv

from ..mergent import Mergent
from .fileReader import CexFileReader
from .apiReader import CexApiReader


class CexMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield CexFileReader(inputPath)
        yield CexApiReader(config['cex'])

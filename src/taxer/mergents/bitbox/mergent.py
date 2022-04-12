from ..mergent import Mergent
from .fileReader import BitBoxFileReader


class BitBoxMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath, transactionsPath):
        yield BitBoxFileReader(inputPath)

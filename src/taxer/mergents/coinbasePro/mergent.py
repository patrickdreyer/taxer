from ..mergent import Mergent
from .fileReader import CoinbaseProFileReader


class CoinbaseProMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath, transactionsPath):
        yield CoinbaseProFileReader(inputPath)

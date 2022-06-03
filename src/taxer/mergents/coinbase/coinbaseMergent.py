from ..mergent import Mergent
from .coinbaseFileReader import CoinbaseFileReader


class CoinbaseMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath, transactionsPath):
        yield CoinbaseFileReader(inputPath)

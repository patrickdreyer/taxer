from ..mergent import Mergent
from .coinbaseFileReader import CoinbaseFileReader


class CoinbaseMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__inputPath = inputPath

    def createReaders(self):
        yield CoinbaseFileReader(self.__inputPath)

from ..mergent import Mergent
from .coinbaseProFileReader import CoinbaseProFileReader


class CoinbaseProMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__inputPath = inputPath

    def createReaders(self):
        yield CoinbaseProFileReader(self.__config, self.__inputPath)

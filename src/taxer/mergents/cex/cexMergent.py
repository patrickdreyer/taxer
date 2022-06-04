from ..mergent import Mergent
from .cexApiReader import CexApiReader
from .cexFileReader import CexFileReader


class CexMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__inputPath = inputPath

    def createReaders(self):
        yield CexFileReader(self.__config, self.__inputPath)
        yield CexApiReader(self.__config)

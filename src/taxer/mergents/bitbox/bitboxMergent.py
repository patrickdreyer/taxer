from ..mergent import Mergent
from .bitboxFileReader import BitboxFileReader


class BitboxMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__inputPath = inputPath

    def createReaders(self):
        yield BitboxFileReader(self.__config, self.__inputPath)

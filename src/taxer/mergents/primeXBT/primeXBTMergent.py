from ..mergent import Mergent
from .primeXBTCovestingFileReader import PrimeXBTCovestingFileReader
from .primeXBTMarginFileReader import PrimeXBTMarginFileReader
from .primeXBTTransferFileReader import PrimeXBTTransferFileReader


class PrimeXBTMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__inputPath = inputPath

    def createReaders(self):
        yield PrimeXBTCovestingFileReader(self.__config, self.__inputPath)
        yield PrimeXBTMarginFileReader(self.__config, self.__inputPath)
        yield PrimeXBTTransferFileReader(self.__config, self.__inputPath)

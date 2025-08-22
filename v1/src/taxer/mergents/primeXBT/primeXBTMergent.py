from ...container import container
from ..mergent import Mergent
from .primeXBTCovestingFileReader import PrimeXBTCovestingFileReader
from .primeXBTMarginFileReader import PrimeXBTMarginFileReader
from .primeXBTTransferFileReader import PrimeXBTTransferFileReader


class PrimeXBTMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        yield PrimeXBTCovestingFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePatterns']['covesting'])
        yield PrimeXBTMarginFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePatterns']['margin'])
        yield PrimeXBTTransferFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePatterns']['transfer'])

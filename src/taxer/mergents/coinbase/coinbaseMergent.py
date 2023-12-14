from ...container import container
from ..mergent import Mergent
from .coinbaseFileReader import CoinbaseFileReader


class CoinbaseMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        yield CoinbaseFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePattern'])

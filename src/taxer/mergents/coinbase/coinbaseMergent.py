from ...container import Container
from ..mergent import Mergent
from .coinbaseFileReader import CoinbaseFileReader


class CoinbaseMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__container = container

    def createReaders(self):
        yield CoinbaseFileReader(self.__container['config']['input'])

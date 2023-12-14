from ...container import container
from ..mergent import Mergent
from .bitboxFileReader import BitboxFileReader


class BitboxMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        yield BitboxFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePattern'])

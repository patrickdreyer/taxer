from ...container import Container
from ..mergent import Mergent
from .bitboxFileReader import BitboxFileReader


class BitboxMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__container = container
        self.__config = config

    def createReaders(self):
        yield BitboxFileReader(self.__config['id'], self.__container['config']['input'], self.__config['fileNamePattern'])

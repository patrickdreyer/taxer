from ...container import Container
from ..mergent import Mergent
from .cexApiReader import CexApiReader
from .cexFileReader import CexFileReader


class CexMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__container = container
        self.__config = config

    def createReaders(self):
        yield CexFileReader(self.__config['id'], self.__container['config']['input'], self.__config['fileNamePattern'])
        yield CexApiReader(self.__config['id'], self.__config['url'], self.__config['userId'], self.__config['key'], self.__config['secret'], self.__config['symbols'])

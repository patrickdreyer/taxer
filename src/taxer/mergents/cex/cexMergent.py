from ...container import container
from ..mergent import Mergent
from .cexApiReader import CexApiReader
from .cexFileReader import CexFileReader


class CexMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        yield CexFileReader(self.__config['id'], container['config']['input'], self.__config['fileNamePattern'])
        yield CexApiReader(self.__config['id'], self.__config['url'], self.__config['userId'], self.__config['key'], self.__config['secret'], self.__config['symbols'])

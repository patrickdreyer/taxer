import os
import re

from .bitbox.mergent import BitBoxMergent
from .cex.mergent import CexMergent
from .coinbasePro.mergent import CoinbaseProMergent


class Mergents:
    def __init__(self, config, path):
        self.__mergents = [BitBoxMergent(), CexMergent(), CoinbaseProMergent()]
        self.__config = config
        self.__path = path

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders(self.__config, self.__path)

from .bitbox.mergent import BitBoxMergent
from .cex.mergent import CexMergent
from .coinbasePro.mergent import CoinbaseProMergent
from .etherscan.mergent import EtherscanMergent
from .primexbt.mergent import PrimeXBTMergent


class Mergents:
    def __init__(self, config, inputPath, cachePath):
        self.__mergents = [BitBoxMergent(), CexMergent(), CoinbaseProMergent(), EtherscanMergent(), PrimeXBTMergent()]
        self.__config = config
        self.__inputPath = inputPath
        self.__cachePath = cachePath

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders(self.__config, self.__inputPath, self.__cachePath)

from .bitbox.bitboxMergent import BitBoxMergent
from .cex.cexMergent import CexMergent
from .coinbasePro.coinbaseProMergent import CoinbaseProMergent
from .etherscan.etherscanMergent import EtherscanMergent
from .primexbt.primexbtMergent import PrimeXBTMergent


class Mergents:
    def __init__(self, config, inputPath, cachePath):
        self.__mergents = [BitBoxMergent(), CexMergent(), CoinbaseProMergent(), EtherscanMergent(), PrimeXBTMergent()]
        self.__config = config
        self.__inputPath = inputPath
        self.__cachePath = cachePath

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders(self.__config['mergents'], self.__inputPath, self.__cachePath)

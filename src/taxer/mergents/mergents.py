from importlib import import_module

from .bitbox.bitboxMergent import BitboxMergent
from .cex.cexMergent import CexMergent
from .coinbasePro.coinbaseProMergent import CoinbaseProMergent
from .etherscan.etherscanMergent import EtherscanMergent
from .primeXBT.primeXBTMergent import PrimeXBTMergent


class Mergents:
    def __init__(self, config, inputPath, cachePath):
        self.__config = config['mergents']
        self.__inputPath = inputPath
        self.__cachePath = cachePath

    def create(self):
        self.__mergents = self.__createMergents()
        return self

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders()

    def __createMergents(self):
        ret = []
        for configKey in self.__config.keys():
            mergentConfig = self.__config[configKey]
            if ('disable' in mergentConfig and mergentConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}Mergent.{}Mergent'.format(configKey, configKey, className)
            clss = Mergents.__importMergent(fullName)
            instance = clss(mergentConfig, self.__inputPath, self.__cachePath)
            ret.append(instance)
        return ret

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)

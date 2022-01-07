from taxer.mergents.etherscan.hexReader import HEXReader

from ..mergent import Mergent
from .apiReader import EtherscanApiReader


class EtherscanMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        hexReader = HEXReader(inputPath)
        yield hexReader
        yield EtherscanApiReader(config['etherscan'], cachePath, hexReader)

import csv

from ..mergent import Mergent
from .apiReader import EtherscanApiReader


class EtherscanMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield EtherscanApiReader(config['etherscan'], cachePath)

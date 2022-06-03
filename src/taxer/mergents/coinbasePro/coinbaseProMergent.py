from ..mergent import Mergent
from .coinbaseProFileReader import CoinbaseProFileReader


class CoinbaseProMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield CoinbaseProFileReader(config['coinbasepro'], inputPath)

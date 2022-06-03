from ..mergent import Mergent
from .cexApiReader import CexApiReader
from .cexFileReader import CexFileReader


class CexMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield CexFileReader(config['cex'], inputPath)
        yield CexApiReader(config['cex'])

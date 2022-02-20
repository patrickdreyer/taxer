from ..mergent import Mergent
from .apiReader import CexApiReader
from .fileReader import CexFileReader


class CexMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield CexFileReader(inputPath)
        yield CexApiReader(config['cex'])
from ..mergent import Mergent
from .fileReader import BitBoxFileReader


class BitBoxMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield BitBoxFileReader(inputPath)

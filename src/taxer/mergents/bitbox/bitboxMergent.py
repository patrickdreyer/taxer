from ..mergent import Mergent
from .bitboxFileReader import BitBoxFileReader


class BitBoxMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield BitBoxFileReader(config['bitbox'], inputPath)

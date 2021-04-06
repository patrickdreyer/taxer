from ..mergent import Mergent
from .fileReader import BitBoxFileReader


class BitBoxMergent(Mergent):
    def createReaders(self, path):
        yield BitBoxFileReader(path)

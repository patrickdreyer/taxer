from ..mergent import Mergent
from .covestingFileReader import PrimeXBTCovestingFileReader
from .marginFileReader import PrimeXBTMarginFileReader
from .transferFileReader import PrimeXBTTransferFileReader


class PrimeXBTMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield PrimeXBTCovestingFileReader(inputPath)
        yield PrimeXBTMarginFileReader(inputPath)
        yield PrimeXBTTransferFileReader(inputPath)

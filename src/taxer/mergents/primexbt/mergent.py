from ..mergent import Mergent
from .covestingFileReader import PrimeXBTCovestingFileReader
from .marginFileReader import PrimeXBTMarginFileReader
from .transferFileReader import PrimeXBTTransferFileReader


class PrimeXBTMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield PrimeXBTCovestingFileReader(config['primexbt'], inputPath)
        yield PrimeXBTMarginFileReader(config['primexbt'], inputPath)
        yield PrimeXBTTransferFileReader(config['primexbt'], inputPath)

from ..mergent import Mergent
from .primexbtCovestingFileReader import PrimeXBTCovestingFileReader
from .primexbtMarginFileReader import PrimeXBTMarginFileReader
from .primexbtTransferFileReader import PrimeXBTTransferFileReader


class PrimeXBTMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        yield PrimeXBTCovestingFileReader(config['primexbt'], inputPath)
        yield PrimeXBTMarginFileReader(config['primexbt'], inputPath)
        yield PrimeXBTTransferFileReader(config['primexbt'], inputPath)

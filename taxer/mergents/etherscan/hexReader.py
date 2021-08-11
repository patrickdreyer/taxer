from ..reader import Reader
from .hexStakeFileReader import HEXStakeFileReader
from .hexTransformationFileReader import HEXTransformationFileReader


class HEXReader(Reader):
    def __init__(self, inputPath):
        self.__stakeFileReader = HEXStakeFileReader(inputPath)
        self.__transformationFileReader = HEXTransformationFileReader(inputPath)

    @property
    def active(self):
        return self.__stakeFileReader.active

    @property
    def history(self):
        return self.__stakeFileReader.history

    @property
    def transformed(self):
        return self.__transformationFileReader.transformed

    def read(self, year):
        yield from self.__stakeFileReader.read(year)
        yield from self.__transformationFileReader.read(year)

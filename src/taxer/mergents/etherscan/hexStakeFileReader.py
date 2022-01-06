import lxml.html as lh

from ..fileReader import FileReader
from .hexStake import HEXStake


class HEXStakeFileReader(FileReader):
    __fileNamePattern = r'.*hex.*stake.*\.html'

    def __init__(self, path):
        super().__init__(path)

    @property
    def active(self):
        return self.__active

    @property
    def history(self):
        return self.__history

    @property
    def filePattern(self):
        return HEXStakeFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        root = lh.parse(filePath)
        tables = root.xpath('//table')
        self.__active = HEXStakeFileReader.__extractStakes(tables[2])
        self.__history = HEXStakeFileReader.__extractStakes(tables[3])
        return list()

    @staticmethod
    def __extractStakes(table):
        ret = list()
        for row in table.xpath("tbody/tr[@class!='divider' and @class!='totals' or not(@class)]"):
            ret.append(HEXStake(row.xpath('td[7]//text()'), row.xpath('td[10]//text()'), row.xpath('td[11]//text()')))
        return ret

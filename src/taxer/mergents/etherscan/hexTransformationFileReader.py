import lxml.html as lh

from ..fileReader import FileReader
from .hexTransformation import HEXTransformation


class HEXTransformationFileReader(FileReader):
    __fileNamePattern = r'.*hex.*transform.*\.html'

    @property
    def transformed(self):
        return self.__transformed

    def __init__(self, path):
        super().__init__(path)

    @property
    def filePattern(self):
        return HEXTransformationFileReader.__fileNamePattern

    def readFile(self, filePath, year):
        root = lh.parse(filePath)
        tables = root.xpath('//table')
        self.__transformed = HEXTransformationFileReader.__extract(tables[0])
        return list()

    @staticmethod
    def __extract(table):
        ret = list()
        for row in table.xpath("tbody/tr[@class!='divider' and @class!='totals' or not(@class)]"):
            ret.append(HEXTransformation(row.xpath('td[6]//text()'), row.xpath('td[7]//text()')))
        return ret

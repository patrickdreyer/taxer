import os
import re

from .bitbox.mergent import BitBoxMergent
from .cex.mergent import CexMergent
from .coinbasePro.mergent import CoinbaseProMergent


class MergentFactory:
    def __init__(self):
        self.__mergents = self.evaluateMergents()

    def createFromPath(self, path):
        for dirPath, _, fileNames in os.walk(path):
            for fileName in fileNames:
                filePath = os.path.join(dirPath, fileName)
                for mergent in self.__mergents:
                    if re.match(mergent.filePattern, fileName, flags=re.IGNORECASE):
                        yield mergent.createReader(filePath)
        
    def evaluateMergents(self):
        return [BitBoxMergent(), CexMergent(), CoinbaseProMergent()]
        # isParserClass = lambda member: inspect.isclass(member) and issubclass(obj, Parser)
        # for _, obj in inspect.getmembers(sys.modules[__name__], isParserClass):
        #     yield obj

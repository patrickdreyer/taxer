import os
import re

from .reader import Reader


class FileReader(Reader):
    def __init__(self, path):
        self.__path = path

    @property
    def filePattern(self): pass
    def readFile(self, filePath): pass

    def read(self):
        for dirPath, _, fileNames in os.walk(self.__path):
            for fileName in fileNames:
                filePath = os.path.join(dirPath, fileName)
                if re.match(self.filePattern, fileName, flags=re.IGNORECASE):
                    yield from self.readFile(filePath)

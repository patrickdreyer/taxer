import os
import re

from .reader import Reader


class FileReader(Reader):
    def __init__(self, id:str, path:str, fileNamePattern:str):
        self.__id = id
        self.__path = path
        self.__fileNamePattern = fileNamePattern

    @property
    def id(self) -> str: return self.__id

    @property
    def filePattern(self) -> str: return self.__fileNamePattern
    
    def readFile(self, filePath, year): pass

    def read(self, year):
        for dirPath, _, fileNames in os.walk(self.__path):
            for fileName in fileNames:
                filePath = os.path.join(dirPath, fileName)
                if re.match(self.filePattern, fileName, flags=re.IGNORECASE):
                    yield from self.readFile(filePath, year)

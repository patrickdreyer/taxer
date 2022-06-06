import os


class CsvFileArray:
    def __init__(self, log, filePath):
        self.__log = log
        self.__dirty = False
        self.__filePath = filePath
        self.__array = []

    def __call__(self):
        return self.__array

    def __len__(self):
        return len(self.__array)

    def __getitem__(self, index):
        return self.__array[index]

    def set(self, value):
        self.__array = value
        self.__dirty = True

    def load(self):
        if not os.path.isfile(self.__filePath):
            self.__log.info("Cache not present; filePath='%s'", self.__filePath)
            return False
        self.__log.info("Load cache; filePath='%s'", self.__filePath)
        with open(self.__filePath, 'r') as file:
            self.__array = map(lambda l: l.replace('\n', ''), file.readlines())
        return True

    def store(self):
        if not self.__dirty:
            self.__log.debug("No changes on cache")
            return
        self.__log.info("Store cache; filePath='%s'", self.__filePath)
        with open(self.__filePath, 'w') as file:
            array = map(lambda v: '{}\n'.format(v), self.__array)
            file.writelines(array)

import csv
import os


class CsvFileDict:
    def __init__(self, log, filePath, columns):
        self.__log = log
        self.__dirty = False
        self.__filePath = filePath
        self.__columns = columns
        self.__dict = {}

    def __call__(self):
        return self.__dict

    def __len__(self):
        return len(self.__dict)

    def __getitem__(self, key):
        return self.__dict[key]

    def __setitem__(self, key, value):
        self.__dict[key] = value
        self.__dirty = True

    def load(self):
        if not os.path.isfile(self.__filePath):
            self.__log.info("Cache not present; filePath='%s'", self.__filePath)
            return False
        self.__log.info("Load cache; filePath='%s'", self.__filePath)
        with open(self.__filePath) as file:
            reader = csv.reader(file, dialect='unix')
            for line in reader:
                self.__dict[line[0]] = line[1]
        return True

    def store(self):
        if not self.__dirty:
            self.__log.debug("No changes on cache")
            return
        self.__log.info("Store cache; filePath='%s'", self.__filePath)
        with open(self.__filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(self.__columns)
            for key, value in self.__dict.items():
                writer.writerow([key, value])

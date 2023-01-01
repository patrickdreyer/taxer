from importlib import import_module

from ..pluginLoader import PluginLoader


class MergentFactory:
    @staticmethod
    def create(config, inputPath, cachePath):
        ret = MergentFactory(config, inputPath, cachePath)
        ret.__createMergents()
        return ret

    def __init__(self, config, inputPath, cachePath):
        self.__config = config['mergents']
        self.__inputPath = inputPath
        self.__cachePath = cachePath

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders()

    def __createMergents(self):
        self.__mergents = PluginLoader.loadByConfig(self.__config, __package__ + '.{}.{}Mergent.{}Mergent', lambda config, clss : clss(config, self.__inputPath, self.__cachePath))

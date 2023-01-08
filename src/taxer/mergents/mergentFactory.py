from importlib import import_module

from ..container import Container
from ..pluginLoader import PluginLoader


class MergentFactory:
    @staticmethod
    def create(container:Container):
        ret = MergentFactory(container)
        ret.__createMergents()
        return ret

    def __init__(self, container:Container):
        self.__container = container

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders()

    def __createMergents(self):
        self.__mergents = PluginLoader.loadByConfig(self.__container['config']['mergents'], __package__ + '.{}.{}Mergent.{}Mergent', lambda config, clss : clss(self.__container, config))

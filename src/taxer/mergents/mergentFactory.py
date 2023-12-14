from ..container import container
from ..pluginLoader import PluginLoader


class MergentFactory:
    @staticmethod
    def create():
        ret = MergentFactory()
        ret.__createMergents()
        return ret

    def createReaders(self):
        for mergent in self.__mergents:
            yield from mergent.createReaders()

    def __createMergents(self):
        self.__mergents = PluginLoader.loadByConfig(container['config']['mergents'], __package__ + '.{}.{}Mergent.{}Mergent', lambda config, clss : clss(config))

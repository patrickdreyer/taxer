from importlib import import_module


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
        self.__mergents = []
        for configKey in self.__config.keys():
            mergentConfig = self.__config[configKey]
            if ('disable' in mergentConfig and mergentConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}Mergent.{}Mergent'.format(configKey, configKey, className)
            clss = MergentFactory.__importMergent(fullName)
            instance = clss(mergentConfig, self.__inputPath, self.__cachePath)
            self.__mergents.append(instance)

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)

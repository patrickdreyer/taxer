from importlib import import_module


class PluginLoader:
    @staticmethod
    def load(config, fullNamePattern, classFactory):
        ret = []
        for key in config.keys():
            itemConfig = config[key]
            if ('disable' in itemConfig and itemConfig['disable']):
                continue
            className = key[0].upper() + key[1:]
            fullName = fullNamePattern.format(key, key, className)
            clss = PluginLoader.__importMergent(fullName)
            instance = classFactory(itemConfig, clss)
            ret.append(instance)
        return ret

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath)
        return getattr(mod, className)

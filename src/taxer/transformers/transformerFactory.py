from importlib import import_module


class TransformerFactory:
    @staticmethod
    def create(config):
        ret = []
        for configKey in config['transformers'].keys():
            transformerConfig = config['transformers'][configKey]
            if ('disable' in transformerConfig and transformerConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}Transformer.{}Transformer'.format(configKey, configKey, className)
            clss = TransformerFactory.__importMergent(fullName)
            instance = clss(transformerConfig)
            ret.append(instance)
        return ret

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)

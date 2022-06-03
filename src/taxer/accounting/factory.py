from importlib import import_module


class AccountingFactory:
    def __init__(self, args, config, currencyConverters):
        self.__args = args
        self.__config = config['accounting']
        self.__currencyConverters = currencyConverters

    def create(self):
        ret = []
        for configKey in self.__config.keys():
            accountingConfig = self.__config[configKey]
            if ('disable' in accountingConfig and accountingConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}Accounting.{}Accounting'.format(configKey, configKey, className)
            clss = AccountingFactory.__importMergent(fullName)
            instance = clss(self.__args.output, accountingConfig, self.__currencyConverters)
            ret.append(instance)
        return ret

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)

from importlib import import_module


class AccountingFactory:
    @staticmethod
    def create(args, config, currencyConverters):
        ret = []
        for configKey in config['accounting'].keys():
            accountingConfig = config['accounting'][configKey]
            if ('disable' in accountingConfig and accountingConfig['disable']):
                continue
            className = configKey[0].upper() + configKey[1:]
            fullName = '.{}.{}Accounting.{}Accounting'.format(configKey, configKey, className)
            clss = AccountingFactory.__importMergent(fullName)
            instance = clss(args.output, accountingConfig, currencyConverters)
            ret.append(instance)
        return ret

    @staticmethod
    def __importMergent(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath, __package__)
        return getattr(mod, className)

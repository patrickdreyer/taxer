from ..pluginLoader import PluginLoader


class AccountingFactory:
    @staticmethod
    def create(args, config, currencyConverters):
        return PluginLoader.loadByConfig(config['accounting'], __package__ + '.{}.{}Accounting.{}Accounting', lambda config, clss: clss(args.output, config, currencyConverters))

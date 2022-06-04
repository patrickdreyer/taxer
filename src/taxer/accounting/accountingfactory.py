from ..pluginLoader import PluginLoader


class AccountingFactory:
    @staticmethod
    def create(args, config, currencyConverters):
        return PluginLoader.load(config['accounting'], __package__ + '.{}.{}Accounting.{}Accounting', lambda config, clss: clss(args.output, config, currencyConverters))

from ..container import container
from ..pluginLoader import PluginLoader


class AccountingFactory:
    @staticmethod
    def create():
        return PluginLoader.loadByConfig(container['config']['accounting'], __package__ + '.{}.{}Accounting.{}Accounting', lambda config, clss: clss(config))

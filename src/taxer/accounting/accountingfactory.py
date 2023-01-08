from ..container import Container
from ..pluginLoader import PluginLoader


class AccountingFactory:
    @staticmethod
    def create(container:Container):
        return PluginLoader.loadByConfig(container['config']['accounting'], __package__ + '.{}.{}Accounting.{}Accounting', lambda config, clss: clss(container, config))

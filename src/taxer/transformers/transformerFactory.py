from ..container import container
from ..pluginLoader import PluginLoader


class TransformerFactory:
    @staticmethod
    def create():
        return PluginLoader.loadByConfig(container['config']['transformers'], __package__ + '.{}.{}Transformer.{}Transformer', lambda config, clss : clss(config))

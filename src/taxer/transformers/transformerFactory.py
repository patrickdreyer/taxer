from ..container import Container
from ..pluginLoader import PluginLoader


class TransformerFactory:
    @staticmethod
    def create(container:Container):
        return PluginLoader.loadByConfig(container['config']['transformers'], __package__ + '.{}.{}Transformer.{}Transformer', lambda config, clss : clss(config))

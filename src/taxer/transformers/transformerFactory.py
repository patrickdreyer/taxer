from ..pluginLoader import PluginLoader


class TransformerFactory:
    @staticmethod
    def create(config):
        return PluginLoader.loadByConfig(config['transformers'], __package__ + '.{}.{}Transformer.{}Transformer', lambda config, clss : clss(config))

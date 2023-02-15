import os

from ..container import Container
from ..pluginLoader import PluginLoader


class ProcessorFactory:
    @staticmethod
    def create(container:Container):
        path = os.path.dirname(__file__)
        ret = PluginLoader.loadFromFiles(path, __package__, '**/*Processor.py', lambda clss: clss(container))
        return ret

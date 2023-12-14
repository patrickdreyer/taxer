import os

from ..container import container
from ..pluginLoader import PluginLoader


class ProcessorFactory:
    @staticmethod
    def create():
        path = os.path.dirname(__file__)
        ret = PluginLoader.loadFromFiles(path, __package__, '**/*Processor.py', lambda clss: clss())
        return ret

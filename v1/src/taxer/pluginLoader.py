import glob
from importlib import import_module
import os


class PluginLoader:
    @staticmethod
    def loadByConfig(config, fullNamePattern, classFactory):
        ret = []
        for key in config.keys():
            itemConfig = config[key]
            if ('disable' in itemConfig and itemConfig['disable']):
                continue
            className = key[0].upper() + key[1:]
            fullName = fullNamePattern.format(key, key, className)
            clss = PluginLoader.__import(fullName)
            instance = classFactory(itemConfig, clss)
            ret.append(instance)
        return ret

    @staticmethod
    def loadFromFiles(path, package, fileNamePattern, classFactory):
        ret = []
        for relativeFileNamePath in glob.iglob(fileNamePattern, root_dir=path, recursive=True):
            fileName = os.path.basename(relativeFileNamePath).replace('.py', '')
            folder = os.path.dirname(relativeFileNamePath).replace('/', '.')
            className = f"{fileName[0].upper()}{fileName[1:]}"
            fullName = f"{package}.{folder}.{fileName}.{className}" if folder else f"{package}.{fileName}.{className}" 
            clss = PluginLoader.__import(fullName)
            instance = classFactory(clss)
            ret.append(instance)
        return ret

    @staticmethod
    def __import(path):
        modulePath, _, className = path.rpartition('.')
        mod = import_module(modulePath)
        return getattr(mod, className)

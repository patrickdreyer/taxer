import os


from ....pluginLoader import PluginLoader

class Contracts(list):
    def __init__(self, etherscanApi):
        self.__etherscanApi = etherscanApi

    def initialize(self):
        path = os.path.dirname(__file__)
        contracts = PluginLoader.loadFromFiles(path, __package__, '*Contracts.py', lambda clss: clss(self.__etherscanApi))
        for contract in contracts:
            self.append(contract)
        return self

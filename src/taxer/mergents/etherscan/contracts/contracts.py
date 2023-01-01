import os


from ....pluginLoader import PluginLoader


class Contracts(dict):
    def __init__(self, etherscanApi):
        self.__invalidAddresses = []
        self.__etherscanApi = etherscanApi

    def initialize(self):
        path = os.path.dirname(__file__)
        contracts = PluginLoader.loadFromFiles(path, __package__, '**/*Contract.py', lambda clss: clss(self, self.__etherscanApi))
        for contract in contracts:
            self[contract.address.lower()] = contract
        return self

    def getByAddress(self, address):
        if address.lower() in self.__invalidAddresses:
            return None
        if address.lower() in self:
            return self[address.lower()]
        contract = self.__etherscanApi.getContract(address)
        if not contract:
            self.__invalidAddresses.append(address.lower())
        return contract

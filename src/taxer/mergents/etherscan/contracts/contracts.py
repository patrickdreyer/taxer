import logging
import os

from ....pluginLoader import PluginLoader


class Contracts(dict):
    def __init__(self, etherscanApi):
        self.__log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
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
        self.__log.warning("Unknown contract; address='%s'", address)
        self.__invalidAddresses.append(address.lower())
        return None

    def getPublicNameTagByAddress(self, address:str):
        contract = self.getByAddress(address)
        return contract.publicNameTag if contract != None else None

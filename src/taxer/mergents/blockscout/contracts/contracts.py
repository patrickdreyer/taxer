import logging
import os

from ....pluginLoader import PluginLoader


class Contracts(dict):
    def __init__(self, accounts:list[str], api):
        self.__log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        self.__invalidAddresses = []
        self.__accounts = accounts
        self.__api = api

    def initialize(self):
        path = os.path.dirname(__file__)
        contracts = PluginLoader.loadFromFiles(path, __package__, '**/*Contract.py', lambda clss: clss(self.__accounts, self.__api))
        for contract in contracts:
            self[contract.address.lower()] = contract
        return self

    def getByAddress(self, address):
        if address.lower() in self.__invalidAddresses:
            return None
        if address.lower() in self:
            return self[address.lower()]
        contract = self.__api.getSmartContract(address)
        self.__log.warning("Unknown contract; address='%s', name='%s', url='https://api.scan.pulsechain.com/api/v2/smart-contracts/%s'", address, contract['name'], address)
        self.__invalidAddresses.append(address.lower())
        return None

    def getPublicNameTagByAddress(self, address:str):
        contract = self.getByAddress(address)
        return contract.publicNameTag if contract != None else None

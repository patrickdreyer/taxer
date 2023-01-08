import json
import os

from ...container import Container
from ..mergent import Mergent
from .contracts.contracts import Contracts
from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader


class EtherscanMergent(Mergent):
    __configFileName = 'etherscan.json'

    def __init__(self, container:Container, config):
        self.__container = container
        self.__config = config
        self.readConfig()

    def createReaders(self):
        etherscanApi = EtherscanApi(self.__config['url'], self.__config['keyToken'], self.__container['config']['cache'], self.__config['publicNameTags'])
        contracts = Contracts(etherscanApi).initialize()
        yield EtherscanApiReader(self.__config['accounts'], etherscanApi, contracts)

    def readConfig(self):
        filePath = os.path.join(os.path.dirname(__file__), EtherscanMergent.__configFileName)
        with open(filePath, 'r') as file:
            self.__config = {**self.__config, **json.load(file)}

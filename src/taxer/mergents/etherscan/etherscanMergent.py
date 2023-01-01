import json
import os
import requests

from .contracts.contracts import Contracts
from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader
from ..mergent import Mergent


class EtherscanMergent(Mergent):
    __configFileName = 'etherscan.json'

    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__cachePath = cachePath
        self.readConfig()

    def createReaders(self):
        with requests.Session() as session:
            etherscanApi = EtherscanApi(self.__config, self.__cachePath, session)
            contracts = Contracts(etherscanApi).initialize()
            yield EtherscanApiReader(self.__config, etherscanApi, contracts)

    def readConfig(self):
        filePath = os.path.join(os.path.dirname(__file__), EtherscanMergent.__configFileName)
        with open(filePath, 'r') as file:
            self.__config = {**self.__config, **json.load(file)}

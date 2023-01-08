from ...container import Container
from ..mergent import Mergent
from .contracts.contracts import Contracts
from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader


class EtherscanMergent(Mergent):
    def __init__(self, container:Container, config):
        self.__container = container
        self.__config = config

    def createReaders(self):
        etherscanApi = EtherscanApi(self.__config['url'], self.__config['keyToken'], self.__container['config']['cache'])
        contracts = Contracts(etherscanApi).initialize()
        yield EtherscanApiReader(self.__config['accounts'], etherscanApi, contracts)

from ...container import container
from ..mergent import Mergent
from .contracts.contracts import Contracts
from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader


class EtherscanMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        accounts = {k.lower():v for k,v in self.__config['accounts'].items()}
        etherscanApi = EtherscanApi(self.__config['url'], self.__config['keyToken'], container['config']['cache'])
        contracts = Contracts(accounts, etherscanApi).initialize()
        yield EtherscanApiReader(accounts, etherscanApi, contracts)

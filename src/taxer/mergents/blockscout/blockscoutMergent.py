from ...container import container
from ..mergent import Mergent
from .contracts.contracts import Contracts
from .blockscoutApi import BlockscoutApi
from .blockscoutApiReader import BlockscoutApiReader


class BlockscoutMergent(Mergent):
    def __init__(self, config):
        self.__config = config

    def createReaders(self):
        accounts = {k.lower():v for k,v in self.__config['accounts'].items()}
        api = BlockscoutApi(self.__config['url'], container['config']['cache'])
        contracts = Contracts(accounts, api).initialize()
        yield BlockscoutApiReader(self.__config['accounts'], api, contracts)

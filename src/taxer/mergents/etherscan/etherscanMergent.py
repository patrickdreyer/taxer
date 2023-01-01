import json
import os
import requests

from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader
from .contracts.axnContract import AxnContract
from .contracts.axn2Contract import Axn2Contract
from .contracts.hexContract import HexContract
from .contracts.hedronContract import HedronContract
from .contracts.fswpContract import FswpContract
from .contracts.metamaskSwapRouterContract import MetamaskSwapRouterContract
from .contracts.uniswapV3PositionsNFT import UniswapV3PositionsNFT
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
            contracts = [
                HexContract.create(etherscanApi),
                HedronContract.create(etherscanApi),
                AxnContract.create(),
                Axn2Contract.create(),
                FswpContract.create(),
                MetamaskSwapRouterContract.create(etherscanApi)
            ]
            yield EtherscanApiReader(self.__config, etherscanApi, contracts)

    def readConfig(self):
        filePath = os.path.join(os.path.dirname(__file__), EtherscanMergent.__configFileName)
        with open(filePath, 'r') as file:
            self.__config = {**self.__config, **json.load(file)}

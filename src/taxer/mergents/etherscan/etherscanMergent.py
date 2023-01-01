import json
import os
import requests

from taxer.mergents.etherscan.tokens.axnToken import AxnToken
from taxer.mergents.etherscan.tokens.hedronToken import HedronToken

from .etherscanApi import EtherscanApi
from .etherscanApiReader import EtherscanApiReader
from .tokens.axnToken import AxnToken
from .tokens.axn2Token import Axn2Token
from .tokens.hexToken import HexToken
from .tokens.hedronToken import HedronToken
from .tokens.fswpToken import FswpToken
from .closedSourceContracts.metamaskSwapRouterContract import MetamaskSwapRouterContract
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
            tokens = [HexToken.create(etherscanApi), HedronToken.create(etherscanApi), AxnToken.create(), Axn2Token.create(), FswpToken.create()]
            closedSourceContracts = [MetamaskSwapRouterContract.create(etherscanApi)]
            yield EtherscanApiReader(self.__config, etherscanApi, tokens, closedSourceContracts)

    def readConfig(self):
        filePath = os.path.join(os.path.dirname(__file__), EtherscanMergent.__configFileName)
        with open(filePath, 'r') as file:
            self.__config = {**self.__config, **json.load(file)}

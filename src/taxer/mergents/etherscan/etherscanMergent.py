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
from ..mergent import Mergent


class EtherscanMergent(Mergent):
    def __init__(self, config, inputPath, cachePath):
        self.__config = config
        self.__cachePath = cachePath

    def createReaders(self):
        with requests.Session() as session:
            etherscanApi = EtherscanApi(self.__config, self.__cachePath, session)
            tokens = [HexToken.create(etherscanApi), HedronToken.create(etherscanApi), AxnToken.create(), Axn2Token.create(), FswpToken.create()]
            yield EtherscanApiReader(self.__config, etherscanApi, tokens)

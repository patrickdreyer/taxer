import requests

from taxer.mergents.etherscan.tokens.axnToken import AxnToken

from .etherscanApi import EtherscanApi
from .apiReader import EtherscanApiReader
from .tokens.axnToken import AxnToken
from .tokens.axn2Token import Axn2Token
from .tokens.hexToken import HexToken
from .tokens.fswpToken import FswpToken
from ..mergent import Mergent


class EtherscanMergent(Mergent):
    def createReaders(self, config, inputPath, cachePath):
        with requests.Session() as session:
            etherscanApi = EtherscanApi(config['etherscan'], cachePath, session)
            tokens = [HexToken.create(etherscanApi), AxnToken.create(), Axn2Token.create(), FswpToken.create()]
            yield EtherscanApiReader(config['etherscan'], etherscanApi, tokens)

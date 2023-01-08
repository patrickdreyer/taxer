from ...container import Container
from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict
from .coinGeckoApi import CoinGeckoApi


class CoinGeckoCurrencyConverter(CurrencyConverter):
    def __init__(self, container:Container, config:any):
        super().__init__(container, config, CoinGeckoApi(config['url']), SymbolDict)

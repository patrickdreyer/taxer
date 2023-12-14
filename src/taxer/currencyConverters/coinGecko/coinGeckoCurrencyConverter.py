from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict
from .coinGeckoApi import CoinGeckoApi


class CoinGeckoCurrencyConverter(CurrencyConverter):
    def __init__(self, config:any):
        super().__init__(config, CoinGeckoApi(config['url']), SymbolDict)

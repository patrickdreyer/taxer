from .coinGeckoApi import CoinGeckoApi
from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict


class CoinGeckoCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        super().__init__(config, cachePath, CoinGeckoApi(config), SymbolDict)

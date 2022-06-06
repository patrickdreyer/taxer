from .exchangeRateHostApi import ExchangeRateHostApi
from ..currencyConverter import CurrencyConverter
from ..symbolArray import SymbolArray


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        super().__init__(config, cachePath, ExchangeRateHostApi(config), SymbolArray)

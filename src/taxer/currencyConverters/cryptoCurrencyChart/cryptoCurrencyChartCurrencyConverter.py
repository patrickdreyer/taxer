from .cryptoCurrencyChartApi import CryptoCurrencyChartApi
from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict


class CryptoCurrencyChartCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        super().__init__(config, cachePath, CryptoCurrencyChartApi(config), SymbolDict)

from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict
from .cryptoCurrencyChartApi import CryptoCurrencyChartApi


class CryptoCurrencyChartCurrencyConverter(CurrencyConverter):
    def __init__(self, config:any):
        super().__init__(config, CryptoCurrencyChartApi(config['url'], config['key'], config['secret']), SymbolDict)

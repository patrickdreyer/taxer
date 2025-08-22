from ..currencyConverter import CurrencyConverter
from ..symbolArray import SymbolArray
from .exchangeRateHostApi import ExchangeRateHostApi


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    def __init__(self, config:any):
        super().__init__(config, ExchangeRateHostApi(config['url'], config['key']), SymbolArray)

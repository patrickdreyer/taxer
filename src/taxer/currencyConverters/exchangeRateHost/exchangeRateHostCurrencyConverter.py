from ...container import Container
from ..currencyConverter import CurrencyConverter
from ..symbolArray import SymbolArray
from .exchangeRateHostApi import ExchangeRateHostApi


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    def __init__(self, container:Container, config:any):
        super().__init__(container, config, ExchangeRateHostApi(config['url'], config['key']), SymbolArray)

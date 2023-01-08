from ...container import Container
from ..currencyConverter import CurrencyConverter
from ..symbolDict import SymbolDict
from .cryptoCurrencyChartApi import CryptoCurrencyChartApi


class CryptoCurrencyChartCurrencyConverter(CurrencyConverter):
    def __init__(self, container:Container, config:any):
        super().__init__(container, config, CryptoCurrencyChartApi(config['url'], config['key'], config['secret']), SymbolDict)

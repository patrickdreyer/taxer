import os

from .exchangeRateHostApi import ExchangeRateHostApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter
from ..dummySymbolMapper import DummySymbolMapper


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        api = ExchangeRateHostApi(config)
        ids = DummySymbolMapper(api)
        super().__init__(config, cachePath, api, ids, config['fileName'])

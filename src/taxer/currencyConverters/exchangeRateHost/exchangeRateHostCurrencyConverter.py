import os

from .exchangeRateHostApi import ExchangeRateHostApi
from ..csvFileArray import CsvFileArray
from ..currencyConverter import CurrencyConverter
from ..symbolArray import SymbolArray


class ExchangeRateHostCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        api = ExchangeRateHostApi(config)
        ids = SymbolArray(CsvFileArray(os.path.join(cachePath, config['idsFileName'])), api)
        super().__init__(config, cachePath, api, ids, config['ratesFileName'])

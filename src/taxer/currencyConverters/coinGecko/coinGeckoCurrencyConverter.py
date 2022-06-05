import os

from .coinGeckoApi import CoinGeckoApi
from ..csvFileDict import CsvFileDict
from ..currencyConverter import CurrencyConverter
from ..symbolMapper import SymbolMapper


class CoinGeckoCurrencyConverter(CurrencyConverter):
    def __init__(self, config, cachePath):
        api = CoinGeckoApi(config)
        ids = SymbolMapper(CsvFileDict(os.path.join(cachePath, config['idsFileName']), ['unit', 'id']), api)
        super().__init__(config, cachePath, api, ids, config['ratesFileName'])

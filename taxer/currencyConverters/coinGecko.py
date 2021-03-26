from .currencyConverter import CurrencyConverter


class CoinGeckoCurrencyConverter(CurrencyConverter):
    def exchangeRate(self, unit):
        return 1.0

    def convert(self, amount, unit):
        return amount * self.exchangeRate(unit)

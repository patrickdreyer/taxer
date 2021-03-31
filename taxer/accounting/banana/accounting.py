import csv

from ...mergents.buyTrade import BuyTrade
from ...mergents.sellTrade import SellTrade
from ..accounting import Accounting
from .accounts import BananaAccounts


class BananaAccounting(Accounting):
    __accounts = None
    __currencyConverter = None
    __transactions = list()

    def __init__(self, currencyConverter):
        self.__accounts = BananaAccounts()
        self.__currencyConverter = currencyConverter

    def transform(self, item):
        date = item.dateTime.date().strftime('%d.%m.%Y')
        cryptoAccount = self.__accounts.get(item.cryptoUnit, item.mergentId)
        fiatAccount = self.__accounts.get(item.fiatUnit, item.mergentId)
        fiatExchangeRate = self.__currencyConverter.exchangeRate(item.fiatUnit, item.dateTime.date())
        cryptoExchangeRate = self.__currencyConverter.exchangeRate(item.cryptoUnit, item.dateTime.date())
        baseCurrencyFiatAmount = round(item.fiatAmount * fiatExchangeRate, 2)
        baseCurrencyFeeAmount = round(item.feeAmount * fiatExchangeRate, 2)
        baseCurrencyTotalAmount = baseCurrencyFiatAmount + baseCurrencyFeeAmount
        cryptoCostCenter = '{0}{1}'.format(item.cryptoUnit, item.mergentId)
        fiatCostCenter = '{0}{1}'.format(item.fiatUnit, item.mergentId)
        if (isinstance(item, BuyTrade)):
            description = 'Kauf; {0}'.format(item.cryptoUnit)
            # fiat                      date, receipt, description, debit,                    credit,                   amount,                           currency,        exchangeRate,       baseCurrencyAmount,      shares, costCenter1
            self.__transactions.append([date, item.id, description, self.__accounts.transfer, fiatAccount,              item.fiatAmount + item.feeAmount, item.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     '-'+fiatCostCenter])
            # crypto
            self.__transactions.append([date, item.id, description, cryptoAccount,            self.__accounts.transfer, item.cryptoAmount,                item.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     cryptoCostCenter])
            # fee
            self.__transactions.append([date, item.id, description, self.__accounts.fees,     self.__accounts.transfer, item.feeAmount,                   item.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])
        elif (isinstance(item, SellTrade)):
            description = 'Verkauf; {0}'.format(item.cryptoUnit)
            # crypto                    date, receipt, description, debit,                    credit,                   amount,            currency,        exchangeRate,       baseCurrencyAmount,      shares, costCenter1
            self.__transactions.append([date, item.id, description, self.__accounts.transfer, cryptoAccount,            item.cryptoAmount, item.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     '-'+cryptoCostCenter])
            # fiat
            self.__transactions.append([date, item.id, description, fiatAccount,              self.__accounts.transfer, item.fiatAmount,   item.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     fiatCostCenter])
            # fee
            self.__transactions.append([date, item.id, description, self.__accounts.fees,     self.__accounts.transfer, item.feeAmount,    item.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])


    def write(self, filePath):
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['date', 'receipt', 'description', 'debit', 'credit', 'amount', 'currency', 'exchangeRate', 'baseCurrencyAmount', 'shares', 'costCenter1'])
            writer.writerows(self.__transactions)

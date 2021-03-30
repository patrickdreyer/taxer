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
        # portfolio,trade id,product,side,created at,size,size unit,price,fee,total,price/fee/total unit
        # default,2985581,BTC-USDC,SELL,2020-11-25T11:29:22.362Z,0.75789000,BTC,19295.00,51.182206425,14572.305343575,USDC
        if (isinstance(item, BuyTrade)):
            description = 'Kauf; {0}'.format(item.debitUnit)
            debitAccount = self.__accounts.get(item.debitUnit, item.mergentId)
            creditAccount = self.__accounts.get(item.creditUnit, item.mergentId)
            debitCostCenter = '{0}{1}'.format(item.debitUnit, item.mergentId)
            creditCostCenter = '-{0}{1}'.format(item.creditUnit, item.mergentId)
        elif (isinstance(item, SellTrade)):
            description = 'Verkauf; {0}'.format(item.creditUnit)
            raise ValueError('Unsupported item')

        date = item.dateTime.date().strftime('%d.%m.%Y')
        # fiat                      date, receipt, description, debit,                    credit,                   amount,            currency,        exchangeRate,                                           baseCurrencyAmount,                                                   shares, costCenter1
        self.__transactions.append([date, item.id, description, self.__accounts.transfer, creditAccount,            item.creditAmount, item.creditUnit, self.__currencyConverter.exchangeRate(item.creditUnit), self.__currencyConverter.convert(item.creditAmount, item.creditUnit), '', creditCostCenter])
        # crypto
        self.__transactions.append([date, item.id, description, debitAccount,             self.__accounts.transfer, item.debitAmount,  item.debitUnit,  self.__currencyConverter.exchangeRate(item.debitUnit),  self.__currencyConverter.convert(item.debitAmount, item.debitUnit),   '', debitCostCenter])
        # fee
        self.__transactions.append([date, item.id, description, self.__accounts.fees,     creditAccount,            item.fee,          item.creditUnit, self.__currencyConverter.exchangeRate(item.creditUnit), self.__currencyConverter.convert(item.fee, item.creditUnit),          '', creditCostCenter])

    def write(self, filePath):
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['date', 'receipt', 'description', 'debit', 'credit', 'amount', 'currency', 'exchangeRate', 'baseCurrencyAmount', 'shares', 'costCenter1'])
            writer.writerows(self.__transactions)

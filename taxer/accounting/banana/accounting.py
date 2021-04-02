import logging
import csv

from ...mergents.trade import Trade
from ...mergents.buyTrade import BuyTrade
from ...mergents.sellTrade import SellTrade
from ...mergents.transfer import Transfer
from ...mergents.depositTransfer import DepositTransfer
from ...mergents.withdrawTransfer import WithdrawTransfer
from ..accounting import Accounting
from .accounts import BananaAccounts


class BananaAccounting(Accounting):
    __log = logging.getLogger(__name__)

    __accounts = None
    __currencyConverter = None
    __transactions = list()

    def __init__(self, currencyConverter):
        self.__accounts = BananaAccounts()
        self.__currencyConverter = currencyConverter

    def transform(self, item):
        date = item.dateTime.date().strftime('%d.%m.%Y')
        if (isinstance(item, Trade)):
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
                self.__log.debug("Create transaction; type=%s, id='%s", 'buy', item.id)
                description = 'Kauf; {0}'.format(item.cryptoUnit)
                # fiat                      date, receipt, description, debit,                    credit,                   amount,                           currency,        exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                self.__transactions.append([date, item.id, description, self.__accounts.transfer, fiatAccount,              item.fiatAmount + item.feeAmount, item.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     '-'+fiatCostCenter])
                # crypto
                self.__transactions.append([date, item.id, description, cryptoAccount,            self.__accounts.transfer, item.cryptoAmount,                item.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     cryptoCostCenter])
                # fee
                self.__transactions.append([date, item.id, description, self.__accounts.fees,     self.__accounts.transfer, item.feeAmount,                   item.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])
            elif (isinstance(item, SellTrade)):
                self.__log.debug("Create transaction; type=%s, id='%s", 'sell', item.id)
                description = 'Verkauf; {0}'.format(item.cryptoUnit)
                # crypto                    date, receipt, description, debit,                    credit,                   amount,            currency,        exchangeRate,       baseCurrencyAmount,      shares, costCenter1
                self.__transactions.append([date, item.id, description, self.__accounts.transfer, cryptoAccount,            item.cryptoAmount, item.cryptoUnit, cryptoExchangeRate, baseCurrencyTotalAmount, '',     '-'+cryptoCostCenter])
                # fiat
                self.__transactions.append([date, item.id, description, fiatAccount,              self.__accounts.transfer, item.fiatAmount,   item.fiatUnit,   fiatExchangeRate,   baseCurrencyFiatAmount,  '',     fiatCostCenter])
                # fee
                self.__transactions.append([date, item.id, description, self.__accounts.fees,     self.__accounts.transfer, item.feeAmount,    item.fiatUnit,   fiatExchangeRate,   baseCurrencyFeeAmount,   '',     ''])
        elif (isinstance(item, Transfer)):
            description = 'Überweisung'
            account = self.__accounts.get(item.unit, item.mergentId)
            exchangeRate = self.__currencyConverter.exchangeRate(item.unit, item.dateTime.date())
            baseCurrencyAmount = round(item.amount * exchangeRate, 2)
            costCenter = '{0}{1}'.format(item.unit, item.mergentId)
            if (isinstance(item, DepositTransfer)):
                self.__log.debug("Create transaction; type=%s, id='%s", 'deposit', item.id)
                # credit                    date, receipt, description, debit,   credit,                 amount,      currency,  exchangeRate, baseCurrencyAmount, shares, costCenter1
                self.__transactions.append([date, item.id, description, account, self.__accounts.equity, item.amount, item.unit, exchangeRate, baseCurrencyAmount, '',     costCenter])
            elif (isinstance(item, WithdrawTransfer)):
                self.__log.debug("Create transaction; type=%s, id='%s", 'withdraw', item.id)
                # debit                     date, receipt, description, debit, credit,  amount,      currency,  exchangeRate, baseCurrencyAmount, shares, costCenter1
                self.__transactions.append([date, item.id, description, '',    account, item.amount, item.unit, exchangeRate, baseCurrencyAmount, '',     '-'+costCenter])

    def write(self, filePath):
        with open(filePath, 'w') as file:
            writer = csv.writer(file, dialect='unix')
            writer.writerow(['date', 'receipt', 'description', 'debit', 'credit', 'amount', 'currency', 'exchangeRate', 'baseCurrencyAmount', 'shares', 'costCenter1'])
            writer.writerows(self.__transactions)

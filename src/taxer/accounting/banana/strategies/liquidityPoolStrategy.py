import logging

from ....transactions.addLiquidity import AddLiquidity
from ....transactions.claimLiquidityFees import ClaimLiquidityFees
from ....transactions.createLiquidityPool import CreateLiquidityPool
from ....transactions.liquidityPool import LiquidityPool
from ....transactions.removeLiquidity import RemoveLiquidity
from ..bananaCurrency import BananaCurrency
from ..bananaStrategy import BananaStrategy


class LiquidityPoolStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def __init__(self, config, accounts, currencyConverters):
        self.__accounts = accounts
        self.__currencyConverters = currencyConverters

    def doesTransform(self, transaction):
        return issubclass(type(transaction), LiquidityPool)

    def transform(self, transaction):
        a0 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount0, transaction)
        a1 = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.amount1, transaction)
        f = BananaCurrency(self.__accounts, self.__currencyConverters, transaction.fee, transaction)
        if isinstance(transaction, CreateLiquidityPool):
            LiquidityPoolStrategy.__log.debug("%s - Provide liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
            description = f"Liquidität bereit stellen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
            # amount0                            date,                          receipt,        description, debit,                     credit,                  amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.liquidity, a0.account,              a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     ''])
            # amount1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.liquidity, a1.account,              a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     ''])
            # fee
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.fees,      f.account,               f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
        elif isinstance(transaction, AddLiquidity):
            LiquidityPoolStrategy.__log.debug("%s - Add liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
            description = f"Liquidität erhöhen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
            # amount0                            date,                          receipt,        description, debit,                     credit,                  amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.liquidity, a0.account,              a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     ''])
            # amount1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.liquidity, a1.account,              a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     ''])
            # fee
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.fees,      f.account,               f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
        elif isinstance(transaction, ClaimLiquidityFees):
            LiquidityPoolStrategy.__log.debug("%s - Claim liquidity fees; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
            description = f"Liquiditätsgebühren einziehen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
            # amount0                            date,                          receipt,        description, debit,                credit,                 amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, a0.account,           self.__accounts.equity, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     a0.costCenter])
            # amount1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, a1.account,           self.__accounts.equity, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     a1.costCenter])
            # fee
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.fees, f.account,              f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
        elif isinstance(transaction, RemoveLiquidity):
            LiquidityPoolStrategy.__log.debug("%s - Remove liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
            description = f"Liquidität auflösen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
            # amount0                            date,                          receipt,        description, debit,                credit,                    amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares, costCenter1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, a0.account,           self.__accounts.liquidity, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, '',     ''])
            # amount1
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, a1.account,           self.__accounts.liquidity, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, '',     ''])
            # fee
            yield (transaction['bananaDate'][0], [transaction['bananaDate'][1], transaction.id, description, self.__accounts.fees, f.account,                 f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  '',     f.costCenter.minus()])
        else:
            LiquidityPoolStrategy.__log.error("Unknown liquidity pool transaction; class='%s'", type(transaction).__name__)
            raise ValueError("Unknown liquidity pool transaction; type='{}'".format(type(transaction)))

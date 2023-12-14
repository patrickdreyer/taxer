import logging

from ....transactions.addLiquidity import AddLiquidity
from ....transactions.claimLiquidityFees import ClaimLiquidityFees
from ....transactions.createLiquidityPool import CreateLiquidityPool
from ....transactions.liquidityPool import LiquidityPool
from ....transactions.removeLiquidity import RemoveLiquidity
from ..bananaStrategy import BananaStrategy


class LiquidityPoolStrategy(BananaStrategy):
    __log = logging.getLogger(__name__)

    def doesTransform(self, transaction):
        return issubclass(type(transaction), LiquidityPool)

    def transform(self, transaction):
        a0 = self._currency(transaction.amount0, transaction)
        l0 = self._currency(transaction.amount0Wrapped, self._accounts.liquidity, transaction.dateTime)
        a1 = self._currency(transaction.amount1, transaction)
        l1 = self._currency(transaction.amount1Wrapped, self._accounts.liquidity, transaction.dateTime)
        f = self._currency(transaction.fee, transaction)
        if isinstance(transaction, CreateLiquidityPool):
            yield from self.__transformCreateLiquidityPool(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, AddLiquidity):
            yield from self.__transformAddLiquidity(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, ClaimLiquidityFees):
            yield from self.__transformClaimLiquidityFees(transaction, a0, l0, a1, l1, f)
        elif isinstance(transaction, RemoveLiquidity):
            yield from self.__transformRemoveLiquidity(transaction, a0, l0, a1, l1, f)
        else:
            LiquidityPoolStrategy.__log.error("Unknown liquidity pool transaction; class='%s'", type(transaction).__name__)
            raise ValueError("Unknown liquidity pool transaction; type='{}'".format(type(transaction)))

    def __transformCreateLiquidityPool(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Provide liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität bereit stellen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # withdrawal0                  description, debit,               credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares
        yield self._book(transaction, [description, '',                  a0.account, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # liquidity0
        yield self._book(transaction, [description, l0.account,          '',         l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # withdrawal1
        yield self._book(transaction, [description, '',                  a1.account, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # liquidity1
        yield self._book(transaction, [description, l1.account,          '',         l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  ''])

    def __transformAddLiquidity(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Add liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität erhöhen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # withdrawal0                  description, debit,               credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares
        yield self._book(transaction, [description, '',                  a0.account, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # liquidity0
        yield self._book(transaction, [description, l0.account,          '',         l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # withdrawal1
        yield self._book(transaction, [description, '',                  a1.account, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # liquidity1
        yield self._book(transaction, [description, l1.account,          '',         l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  ''])

    def __transformClaimLiquidityFees(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Claim liquidity fees; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquiditätsgebühren einziehen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # amount0                      description, debit,               credit,                amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares
        yield self._book(transaction, [description, a0.account,          self._accounts.equity, a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # amount1
        yield self._book(transaction, [description, a1.account,          self._accounts.equity, a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,             f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  ''])

        # interest                    description,     amount,    currency, exchangeRate,                 baseCurrencyAmount
        self._interest(transaction, ['Liquidity Pool', l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, l0.baseCurrency.amount])
        self._interest(transaction, ['Liquidity Pool', l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, l1.baseCurrency.amount])

    def __transformRemoveLiquidity(self, transaction, a0, l0, a1, l1, f):
        LiquidityPoolStrategy.__log.debug("%s - Remove liquidity; %s, %s/%s", transaction.dateTime, transaction.poolId, a0, a1)
        description = f"Liquidität auflösen; {transaction.poolId}: {transaction.amount0.unit}/{transaction.amount1.unit}"
        # deposit0                     description, debit,               credit,     amount,    currency, exchangeRate,                 baseCurrencyAmount,     shares
        yield self._book(transaction, [description, a0.account,          '',         a0.amount, a0.unit,  a0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # liquidity0
        yield self._book(transaction, [description, '',                  l0.account, l0.amount, l0.unit,  l0.baseCurrency.exchangeRate, a0.baseCurrency.amount, ''])
        # deposit1
        yield self._book(transaction, [description, a1.account,          '',         a1.amount, a1.unit,  a1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # liquidity1
        yield self._book(transaction, [description, '',                  l1.account, l1.amount, l1.unit,  l1.baseCurrency.exchangeRate, a1.baseCurrency.amount, ''])
        # fee
        yield self._book(transaction, [description, self._accounts.fees, f.account,  f.amount,  f.unit,   f.baseCurrency.exchangeRate,  f.baseCurrency.amount,  ''])

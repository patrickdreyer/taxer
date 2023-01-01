from datetime import datetime
from dateutil import parser
from pytz import utc

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.sellTrade import SellTrade
from ...transactions.withdrawTransfer import WithdrawTransfer


class PoloniexApiReader(Reader):
    __limit = 1000

    def __init__(self, id, api):
        self.__id = id
        self.__api = api

    def read(self, year):
        start = int(round(datetime(year, 1, 1, tzinfo=utc).timestamp()))
        end = int(round(datetime(year, 12, 31, tzinfo=utc).timestamp()))
        yield from self.__fetchTransactions(start, end)
        yield from self.__fetchFills(start, end)

    def __fetchTransactions(self, start, end):
        since = start
        while since < end:
            transactions = self.__api.fetchTransactions(since=since, limit=PoloniexApiReader.__limit)
            if not len(transactions):
                break
            transactions = (self.__transformTransfers(t) for t in iter(transactions))
            for transfer in transactions:
                since = transfer['timestamp'] + 1
                amount = Currency(transfer['currency'], transfer['amount'])
                fee = Currency(transfer['fee']['currency'], transfer['fee']['cost'])
                if transfer['type'] == 'withdrawal':
                    yield WithdrawTransfer(self.__id, transfer['dateTime'], transfer['id'], amount, fee, None)
                elif transfer['type'] == 'deposit':
                    yield DepositTransfer(self.__id, transfer['dateTime'], transfer['id'], amount, fee, None)

    def __fetchFills(self, start, end):
        since = start
        while since < end:
            fills = self.__api.fetch_my_trades(since=since, limit=PoloniexApiReader.__limit)
            if not len(fills):
                break
            for fill in fills:
                since = fill['timestamp'] + 1
                symbols = fill['symbol'].split('/')
                symbol1 = Currency(symbols[0], fill['amount'])
                symbol2 = Currency(symbols[1], fill['cost'])
                fee = Currency(fill['fee']['currency'], fill['fee']['cost'])
                if fill['side'] == 'sell':
                    yield SellTrade(self.__id, fill['dateTime'], fill['id'], symbol1, symbol2, fee)
                elif fill['side'] == 'buy':
                    yield BuyTrade(self.__id, fill['dateTime'], fill['id'], symbol1, symbol2, fee)

    def __transformTransfers(self, transfer):
        transfer['dateTime'] = parser.isoparse(transfer['datetime'])
        return transfer

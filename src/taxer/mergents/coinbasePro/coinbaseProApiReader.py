import datetime
import pytz

from ..reader import Reader
from ...transactions.buyTrade import BuyTrade
from ...transactions.currency import Currency
from ...transactions.sellTrade import SellTrade
from ...transactions.depositTransfer import DepositTransfer
from ...transactions.withdrawTransfer import WithdrawTransfer


class CoinbaseProApiReader(Reader):
    def __init__(self, config, api):
        self.__config = config
        self.__api = api

    def read(self, year):
        accounts = self.__api.getAllAccounts()
        if len(accounts) == 0:
            return

        profileId = accounts[0]['profile_id']
        transfers = self.__api.getAllTransfers(profileId)
        transfers = (self.__transformTransfers(accounts, t) for t in iter(transfers))
        for transfer in transfers:
            if transfer['type'] == 'withdraw':
                if transfer['dateTime'].year != year:
                    continue
                fee = Currency(transfer['currency'], 0)
                # even if fee is given in transfer, CBP does not deduce it
                # if 'fee' in transfer['details']:
                #     fee = Currency(transfer['currency'], transfer['details']['fee'])
                yield WithdrawTransfer(self.__config['id'], transfer['dateTime'], transfer['id'], Currency(transfer['currency'], transfer['amount']), fee)
            elif transfer['type'] == 'deposit':
                if transfer['dateTime'].year != year:
                    continue
                    fee = Currency(transfer['currency'], 0)
                    if 'fee' in transfer['details']:
                        fee = Currency(transfer['currency'], transfer['details']['fee'])
                    yield DepositTransfer(self.__config['id'], transfer['dateTime'], transfer['id'], Currency(transfer['currency'], transfer['amount']), fee)

    def __transformTransfers(self, accounts, transfer):
        transfer['currency'] = [a['currency'] for a in accounts if a['id'] == transfer['account_id']][0]
        transfer['dateTime'] = pytz.utc.localize(datetime.datetime.strptime(transfer['completed_at'].replace('+00', ''), '%Y-%m-%d %H:%M:%S.%f'))
        return transfer

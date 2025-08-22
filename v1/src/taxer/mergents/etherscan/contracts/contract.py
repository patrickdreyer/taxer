from ..ether import Ether
from ....transactions.currency import Currency
from ....transactions.depositTransfer import DepositTransfer
from ....transactions.withdrawTransfer import WithdrawTransfer


class Contract:
    def __init__(self, address:str, publicNameTag:str, accounts:list[str], ):
        self.__address = address
        self.__publicNameTag = publicNameTag
        self.__accounts = accounts

    @property
    def address(self) -> str: return self.__address

    @property
    def publicNameTag(self) -> str: return self.__publicNameTag

    @property
    def web3Contract(self): pass

    def getMergendIdByAddress(self, address:str):
        address = address.lower()
        if not address in self.__accounts:
            return None
        return self.__accounts[address];

    def processErc20Transfer(self, address, id, year, erc20Transaction):
        if erc20Transaction['dateTime'].year != year:
            return

        amount = self.amount(erc20Transaction['value'])
        if address.lower() == erc20Transaction['from'].lower():
            toId  = self.getMergendIdByAddress(erc20Transaction['to'])
            yield WithdrawTransfer(id, erc20Transaction['dateTime'], erc20Transaction['hash'], amount, Ether.feeFromTransaction(erc20Transaction), address)
            if toId != None:
                yield DepositTransfer(toId, erc20Transaction['dateTime'], erc20Transaction['hash'], amount, Ether.zero(), erc20Transaction['to'])
        elif address.lower() == erc20Transaction['to'].lower():
            fromId  = self.getMergendIdByAddress(erc20Transaction['from'])
            if fromId != None:
                yield WithdrawTransfer(fromId, erc20Transaction['dateTime'], erc20Transaction['hash'], amount, Ether.feeFromTransaction(erc20Transaction), erc20Transaction['from'])
            yield DepositTransfer(id, erc20Transaction['dateTime'], erc20Transaction['hash'], amount, Ether.zero(), address)
    
    def processTransaction(self, id, year, transaction, erc20Transaction): pass
    def amount(self, value) -> Currency: pass

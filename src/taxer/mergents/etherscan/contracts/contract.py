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
    
    def processTransaction(self, id, year, transaction, erc20Transaction): pass

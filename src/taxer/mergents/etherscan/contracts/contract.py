class Contract:
    def __init__(self, address:str, publicNameTag:str):
        self.__address = address
        self.__publicNameTag = publicNameTag

    @property
    def address(self) -> str: return self.__address

    @property
    def publicNameTag(self) -> str: return self.__publicNameTag

    @property
    def web3Contract(self): pass

    def processTransaction(self, id, year, transaction, erc20Transaction): pass

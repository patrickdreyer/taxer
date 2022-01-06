import logging


class Ignore:
    __log = logging.getLogger(__name__)

    def __init__(self, entries):
        self.__entries = entries

    def transform(self, transactions):
        return filter(self.__filterIgnored, transactions)

    def __filterIgnored(self, transaction):
        if transaction.id in self.__entries:
            Ignore.__log.info("Ignore transaction; %s", transaction)
            return False
        return True

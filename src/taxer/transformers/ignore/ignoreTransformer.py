import logging

from ..transformer import Transformer


class IgnoreTransformer(Transformer):
    __log = logging.getLogger(__name__)

    def __init__(self, config):
        self.__config = config

    def transform(self, transactions):
        return filter(self.__filterIgnored, transactions)

    def __filterIgnored(self, transaction):
        if transaction.id in self.__config:
            IgnoreTransformer.__log.info("Ignore transaction; %s", transaction)
            return False
        return True

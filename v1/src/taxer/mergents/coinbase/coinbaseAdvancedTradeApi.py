from datetime import datetime, timezone
from coinbase.rest import RESTClient


# https://docs.cdp.coinbase.com/advanced-trade/docs/sdk-overview
class CoinbaseAdvancedTradeApi:
    def __init__(self, symbols:list[str], keyName:str, keySecret:str):
        self.__symbols = symbols
        self.__client = RESTClient(keyName, keySecret, rate_limit_headers=True)

    def getFills(self, year):
        startSequenceTimestamp = datetime(year-1, 12, 31, 23, 59, 59, tzinfo=timezone.utc).isoformat()
        endSequenceTimestamp = datetime(year+1, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        yield from self.__getPaginated(lambda cursor: self.__client.get_fills(cursor=cursor, start_sequence_timestamp=startSequenceTimestamp, end_sequence_timestamp=endSequenceTimestamp))

    def __getPaginated(self, action):
        cursor = None
        while True:
            response = action(cursor)
            cursor = response.cursor
            for item in response.fills:
                if any(symbol in item['product_id'] for symbol in self.__symbols):
                    yield item.to_dict()
            if len(response.cursor) == 0:
                break

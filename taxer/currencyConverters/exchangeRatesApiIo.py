import requests
import json


class ExchangeRatesApiIo:
    def exchangeRate(self, unit, date):
        response = requests.get('https://api.exchangeratesapi.io/{0}?base=CHF'.format(date.strftime('%Y-%m-%d')))
        content = json.loads(response.text)
        rates = content['rates']
        return float(rates[unit])

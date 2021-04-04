class BananaAccounts:
    __map = {
        'BTC': {
            'BB2': '1000',
            'CB' : '1002',
            'CBP': '1003',
            'CEX': '1004'
        },
        'ETH': {
            'BB2': '1010',
            'CP' : '1012',
            'CBP': '1013',
            'MM' : '1015',
            'HL' : '1016'
        },
        'HEX': {
            'MM' : '1020',
            'SK' : '1021'
        },
        'XRP': {
            'CBP': '1043'
        },
        'AXN': {
            'MM' : '1050',
            'SK' : '1051'
        },
        'EUR': {
            'CP' : '1110',
            'CBP': '1111'
        },
        'USD': {
            'CEX' : '1120'
        },
        'USDC': {
            'CBP' : '1121'
        }
    }

    @property
    def transfer(self):
        return '1100'

    @property
    def equity(self):
        return '200'

    @property
    def fees(self):
        return '319'

    def get(self, unit, mergentId):
        u = BananaAccounts.__map[unit]
        m = u[mergentId]
        return m

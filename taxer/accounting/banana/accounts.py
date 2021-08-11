class BananaAccounts:
    __map = {
        'BTC': {
            'S':   '1000',
            'S32': '1001',
            'LB':  '1002',
            'CB' : '1003',
            'CBP': '1004',
            'CEX': '1005',
            'M'  : '1006',
            'PRM': '1007'
        },
        'ETH': {
            'S':   '1010',
            'CB' : '1012',
            'CBP': '1013',
            'HEX': '1016',
            'MM' : '1015'
        },
        'HEX': {
            'ETH': '1016',
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
            'CB' : '1110',
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

    @property
    def staked(self):
        return 'SK'

    def get(self, unit, mergentId):
        u = BananaAccounts.__map[unit]
        m = u[mergentId]
        return m

from pytest import mark

from taxer.mergents.etherscan.ether import Ether


class TestEther:
    @mark.parametrize("value, expected", [
        (10, '0x000000000000000000000000000000000000000000000000000000000000000a'),
        ('10', '0x000000000000000000000000000000000000000000000000000000000000000a'),
        ('0x10', '0x0000000000000000000000000000000000000000000000000000000000000010'),
    ])
    def test_toTopic(self, value, expected):
        # act
        actual = Ether.toTopic(value)

        # assert
        assert actual == expected

from taxer.mergents.blockscout.pulse import Pulse


class TestPulse:
    def test_decodeContractInput(self):
        decodedInput = {'method_call': 'transfer(address recipient, uint256 amount)', 'method_id': 'a9059cbb', 'parameters': [{'name': 'recipient', 'type': 'address', 'value': '0xf0f66cce56c4da6aac...facc4e94ff'}, {'name': 'amount', 'type': 'uint256', 'value': '908196488291'}]}
        expected = ('transfer', {'recipient': '0xf0f66cce56c4da6aac...facc4e94ff', 'amount': '908196488291'})

        # act
        actual = Pulse.decodeContractInput(decodedInput)

        # assert
        assert actual == expected

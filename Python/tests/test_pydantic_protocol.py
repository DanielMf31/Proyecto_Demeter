import unittest
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import SetGpio, SetPwm, ExecSequence, SequenceStep, CmdId

class TestPydanticProtocol(unittest.TestCase):
    def setUp(self):
        self.protocol = DemeterProtocolV2()

    def test_serialize_deserialize_set_gpio(self):
        # 1. Create Object
        cmd = SetGpio(target_id=10, pin=4, value=1, flags=0)
        
        # 2. Serialize
        frame = self.protocol.serialize(cmd)
        
        # 3. Deserialize
        decoded_cmd = self.protocol.parse_frame(frame)
        
        # 4. Verify
        self.assertIsInstance(decoded_cmd, SetGpio)
        self.assertEqual(decoded_cmd.target_id, 10)
        self.assertEqual(decoded_cmd.pin, 4)
        self.assertEqual(decoded_cmd.value, 1)

    def test_serialize_deserialize_sequence(self):
        # 1. Create Sequence
        steps = [
            SequenceStep(target_id=10, cmd_id=CmdId.SET_GPIO, pin=4, value=1, delay_ms=100),
            SequenceStep(target_id=10, cmd_id=CmdId.SET_GPIO, pin=4, value=0, delay_ms=0)
        ]
        seq = ExecSequence(target_id=20, steps=steps)
        
        # 2. Serialize
        frame = self.protocol.serialize(seq)
        
        # 3. Deserialize
        decoded_cmd = self.protocol.parse_frame(frame)
        
        # 4. Verify
        self.assertIsInstance(decoded_cmd, ExecSequence)
        self.assertEqual(len(decoded_cmd.steps), 2)
        self.assertEqual(decoded_cmd.steps[0].delay_ms, 100)

    def test_bad_crc_returns_none(self):
        cmd = SetGpio(target_id=10, pin=4, value=1)
        frame = bytearray(self.protocol.serialize(cmd))
        
        # Corrupt Last Byte (CRC)
        frame[-1] = (frame[-1] + 1) % 256
        
        decoded = self.protocol.parse_frame(frame)
        self.assertIsNone(decoded)

if __name__ == '__main__':
    unittest.main()

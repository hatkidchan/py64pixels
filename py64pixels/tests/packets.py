import unittest
from io import BytesIO
from py64pixels.packets import *
from py64pixels.packets.constants import *

PKT_LOGIN = '01 fffffda8 000000c9 0a 6861746b69646368616e 002a'
PKT_CHAT = '41 34 0d 68656c6c6f2c20776f726c6421'
PKT_RELATIVE_MOVE = '2c 02  2d 02  2e 02  2f 02  21 02 fc 08'
PKT_ABS_MOVE = '24 02 fffffda8 000000c9'
PKT_BULLET = '70 fffffda8 000000c9 7f'
PKT_PLACE_BLOCK_MAP = '33 fffffda8 000000c9 00 30 7f'
PKT_CLEAR_BLOCK_MAP = '34 fffffda8 000000c9'
PKT_RAYCAST = '82  81'
PKT_SOUND = '60 fc 08 7f'
PKT_PULL = 'e2 fffffda8 000000c9 00ff 007f fc 08'
PKT_PUSH = 'e1 fffffda8 000000c9 00ff 007f fc 08'
PKT_PING = 'f0'
PKT_PONG = 'f1'
PKT_STEP = '2a fffffda8 000000c9  2b fffffda8 000000c9'
PKT_PLACE_BLOCK_PLAYER = '31 02 fffffda8 000000c9 01 30 7f'
PKT_SPAWN = '20 7f 0a 6861746b69646368616e fffffda8 000000c9 68 7f'
PKT_DESPAWN = '22 02'
PKT_DATA_START = '11 07 fffffda8 000000c9 0000000a'
PKT_DATA_CHUNK = '12 000a 30313233343536373839'
PKT_DATA_END = '13'
PKT_DATA_FULL = PKT_DATA_START + PKT_DATA_CHUNK + PKT_DATA_END
PKT_NICK = '26 02 0a 6861746b69646368616e'
PKT_KICK = 'f5 0a 596f75206964696f7421'
PKT_HEALTH = '91 04'
PKT_PVP = '92 01'
PKT_OP = '28 002a'
PKT_PLACE_PUSHABLE_PLAYER = '32 02 fffffda8 000000c9 ff 00 30 7f'


class TestPacketsAutoDecoding(unittest.TestCase):
    
    def test_garbage_read(self):
        with PacketReader(bytes.fromhex('00000000' + PKT_LOGIN)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, LoginPacket)
            self.assertEqual(pr.junk, b'')

    def test_multiple(self):
        with PacketReader(bytes.fromhex(PKT_LOGIN + PKT_CHAT)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, LoginPacket)
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, ChatPacket)
            self.assertEqual(pr.junk, b'')
    
    def test_login(self):
        with PacketReader(bytes.fromhex(PKT_LOGIN)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, LoginPacket)
            self.assertEqual(pkt.head, PKID_LOGIN)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pkt.name, 'hatkidchan')
            self.assertTrue(pkt.op)
            self.assertEqual(pr.junk, b'')
    
    def test_chat(self):
        with PacketReader(bytes.fromhex(PKT_CHAT)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, ChatPacket)
            self.assertEqual(pkt.head, PKID_CHAT)
            self.assertEqual(pkt.user_id, 0x34)
            self.assertEqual(pkt.text, 'hello, world!')
            self.assertEqual(pr.junk, b'')
            
    def test_relative_move(self):
        with PacketReader(bytes.fromhex(PKT_RELATIVE_MOVE)) as pr:
            for (edx, edy) in RelativeMovePacket.COMPRESSED_MOVES:
                pkt = decoder.read_one(pr)
                self.assertIsInstance(pkt, RelativeMovePacket)
                self.assertEqual(pkt.player_id, 2)
                self.assertEqual(pkt.dx, edx)
                self.assertEqual(pkt.dy, edy)
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, RelativeMovePacket)
            self.assertEqual(pkt.player_id, 2)
            self.assertEqual(pkt.dx, -4)
            self.assertEqual(pkt.dy, 8)
            self.assertEqual(pr.junk, b'')
    
    def test_raycast(self):
        with PacketReader(bytes.fromhex(PKT_RAYCAST)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, RaycastChangePacket)
            self.assertTrue(pkt.enabled)
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, RaycastChangePacket)
            self.assertFalse(pkt.enabled)
            self.assertEqual(pr.junk, b'')
            
    def test_absolute_move(self):
        with PacketReader(bytes.fromhex(PKT_ABS_MOVE)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, AbsoluteMovePacket)
            self.assertEqual(pkt.user_id, 2)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pr.junk, b'')
            
    def test_bullet(self):
        with PacketReader(bytes.fromhex(PKT_BULLET)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, BulletPacket)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pkt.type, 127)
            self.assertEqual(pr.junk, b'')
    
    def test_place_block_map(self):
        with PacketReader(bytes.fromhex(PKT_PLACE_BLOCK_MAP)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PlaceBlockMapPacket)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pkt.type, 0)
            self.assertEqual(pkt.char, b'0')
            self.assertEqual(pkt.color, 127)
            self.assertEqual(pr.junk, b'')
    
    def test_clear_block_map(self):
        with PacketReader(bytes.fromhex(PKT_CLEAR_BLOCK_MAP)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, ClearBlockMapPacket)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pr.junk, b'')

    def test_sound(self):
        with PacketReader(bytes.fromhex(PKT_SOUND)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, SoundPacket)
            self.assertEqual(pkt.rel_x, -4)
            self.assertEqual(pkt.rel_y, 8)
            self.assertEqual(pkt.value, 127)
            self.assertEqual(pr.junk, b'')

    def test_pull(self):
        with PacketReader(bytes.fromhex(PKT_PULL)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PullPacket)
            self.assertEqual(pkt.start_x, -600)
            self.assertEqual(pkt.start_y, 201)
            self.assertEqual(pkt.size_x, 255)
            self.assertEqual(pkt.size_y, 127)
            self.assertEqual(pkt.move_x, -4)
            self.assertEqual(pkt.move_y, 8)
            self.assertEqual(pr.junk, b'')
            
    def test_push(self):
        with PacketReader(bytes.fromhex(PKT_PUSH)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PushPacket)
            self.assertEqual(pkt.start_x, -600)
            self.assertEqual(pkt.start_y, 201)
            self.assertEqual(pkt.size_x, 255)
            self.assertEqual(pkt.size_y, 127)
            self.assertEqual(pkt.move_x, -4)
            self.assertEqual(pkt.move_y, 8)
            self.assertEqual(pr.junk, b'')

    def test_pingpong(self):
        with PacketReader(bytes.fromhex(PKT_PING + PKT_PONG)) as pr:
            self.assertIsInstance(decoder.read_one(pr), PingPacket)
            self.assertIsInstance(decoder.read_one(pr), PongPacket)
            self.assertEqual(pr.junk, b'')

    def test_step(self):
        with PacketReader(bytes.fromhex(PKT_STEP)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, StepPacket)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertFalse(pkt.on)
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, StepPacket)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertTrue(pkt.on)
            self.assertEqual(pr.junk, b'')
            
    def test_place_block_player(self):
        with PacketReader(bytes.fromhex(PKT_PLACE_BLOCK_PLAYER)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PlaceBlockPlayerPacket)
            self.assertEqual(pkt.player_id, 2)
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pkt.type, 1)
            self.assertEqual(pkt.char, b'0')
            self.assertEqual(pkt.color, 127)
            self.assertEqual(pr.junk, b'')

    def test_spawn_despawn(self):
        with PacketReader(bytes.fromhex(PKT_SPAWN + PKT_DESPAWN)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, SpawnPacket)
            self.assertEqual(pkt.player_id, 127)
            self.assertEqual(pkt.name, 'hatkidchan')
            self.assertEqual(pkt.x, -600)
            self.assertEqual(pkt.y, 201)
            self.assertEqual(pkt.char, b'h')
            self.assertEqual(pkt.color, 127)
            
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, DespawnPacket)
            self.assertEqual(pkt.player_id, 2)
            self.assertEqual(pr.junk, b'')

    def test_data(self):
        with PacketReader(bytes.fromhex(PKT_DATA_FULL)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, DataStartPacket)
            self.assertEqual(pkt.chunk_type, 7)
            self.assertEqual(pkt.chunk_x, -600)
            self.assertEqual(pkt.chunk_y, 201)
            self.assertEqual(pkt.data_length, 10)
            
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, DataChunkPacket)
            self.assertEqual(pkt.data, b'0123456789')
            
            self.assertIsInstance(decoder.read_one(pr), DataEndPacket)
            
            self.assertEqual(pr.junk, b'')

    def test_nick(self):
        with PacketReader(bytes.fromhex(PKT_NICK)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PlayerNicknamePacket)
            self.assertEqual(pkt.player_id, 2)
            self.assertEqual(pkt.name, 'hatkidchan')
            self.assertEqual(pr.junk, b'')

    def test_kick(self):
        with PacketReader(bytes.fromhex(PKT_KICK)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, KickPacket)
            self.assertEqual(pkt.reason, 'You idiot!')
            self.assertEqual(pr.junk, b'')

    def test_health(self):
        with PacketReader(bytes.fromhex(PKT_HEALTH)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, HealthPacket)
            self.assertEqual(pkt.value, 4)
            self.assertEqual(pr.junk, b'')

    def test_pvp(self):
        with PacketReader(bytes.fromhex(PKT_PVP)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PVPPacket)
            self.assertTrue(pkt.enabled)
            self.assertEqual(pr.junk, b'')

    def test_op(self):
        with PacketReader(bytes.fromhex(PKT_OP)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, OperatorPacket)
            self.assertTrue(pkt.status)
            self.assertEqual(pr.junk, b'')

    def test_place_pushable_player(self):
        with PacketReader(bytes.fromhex(PKT_PLACE_PUSHABLE_PLAYER)) as pr:
            pkt = decoder.read_one(pr)
            self.assertIsInstance(pkt, PlacePushablePlayerPacket)
            self.assertEqual(pkt.player_id, 2)
            self.assertEqual(pkt.target_x, -600)
            self.assertEqual(pkt.target_y, 201)
            self.assertEqual(pkt.delta_x, -1)
            self.assertEqual(pkt.delta_y, 0)
            self.assertEqual(pkt.char, b'0')
            self.assertEqual(pkt.color, 127)
            self.assertEqual(pr.junk, b'')


class TestPacketReader(unittest.TestCase):
    
    def test_junk(self):
        with PacketReader(bytes.fromhex(PKT_LOGIN + 'aabbccdd')) as pr:
            pkt = decoder.read_one(pr)
            self.assertEqual(pr.junk, b'\xaa\xbb\xcc\xdd')


if __name__ == '__main__':
    unittest.main()


from typing import ClassVar, Tuple, List
from ctypes import *
from py64pixels.packets.utils import *
from py64pixels.packets.base import BasePacket
from py64pixels.packets.constants import *

decoder = PacketDecoder()

__all__ = [ 'decoder', 'PacketReader' ]

@decoder.register
class LoginPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_LOGIN
    x: c_int32
    y: c_int32
    name: str8
    op: bool42


@decoder.register
class ChatPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_CHAT
    user_id: c_int8
    text: str8


@decoder.register
class AbsoluteMovePacket(BasePacket):
    head: ClassVar[c_int8] = PKID_MOVE_ABSOLUTE
    user_id: c_int8
    x: c_int32
    y: c_int32


@decoder.register
class BulletPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_BULLET
    x: c_int32
    y: c_int32
    type: c_uint8
    

@decoder.register
class PlaceBlockMapPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PLACE_BLOCK_MAP
    x: c_int32
    y: c_int32
    type: c_int8
    char: c_char
    color: c_uint8


@decoder.register
class ClearBlockMapPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_CLEAR_BLOCK_MAP
    x: c_int32
    y: c_int32


@decoder.register
class RaycastChangePacket(BasePacket):
    head: ClassVar[Tuple[c_int8]] = (PKID_RAYCAST_ON, PKID_RAYCAST_OFF)

    @classmethod
    def read_from(cls, pr: PacketReader) -> BasePacket:
        pkt = BasePacket.read_from(pr)
        return cls(pkt._raw, enabled=pkt._raw[0] == PKID_RAYCAST_ON)

@decoder.register
class RelativeMovePacket(BasePacket):
    head: ClassVar[Tuple[c_int8]] = PKID_MOVE_COMPRESSED + (PKID_MOVE_DELTA,)
    COMPRESSED_MOVES: ClassVar[List[Tuple[int, int]]] = [
            (-1, 0), (1, 0), (0, -1), (0, 1)
    ]
    player_id: c_int8
    dx: c_int8
    dy: c_int8
    
    @classmethod
    def read_from(cls, pr: PacketReader) -> BasePacket:
        with pr.atomic() as r:
            r.seek(r.tell() - 1)
            head = r.read(1)
            player_id = r.read_one(c_int8)
            if head[0] in PKID_MOVE_COMPRESSED:
                dx, dy = cls.COMPRESSED_MOVES[head[0] & 0x03]
            else:
                dx, dy = r.read_one(c_int8), r.read_one(c_int8)
            raw_data = head + r.read_since_init()
            return cls(_raw=raw_data, player_id=player_id, dx=dx, dy=dy)
    
@decoder.register
class SoundPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PLAY_SOUND
    note_names: ClassVar[List[str]] = [
        'kick', 'snare', 'hihat_closed', 'hihat_open',
        'tom_high', 'tom_middle', 'tom_low', 'crash'
    ]
    note_freqs: ClassVar[List[float]] = [
        3520, 7040, 7040, 300, 200, 120, 7040
    ]
    rel_x: c_int8
    rel_y: c_int8
    value: c_uint8
    
    @property
    def note_type(self):
        if self.value < 240:
            return 'note'
        return self.note_names[self.value - 240]
        
    @property
    def freq(self):
        if self.value < 240:
            return 440 * (2 ** ((self.value - 114) / 24))
        return self.note_freqs[self.value - 240]


@decoder.register
class PullPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PULL
    start_x: c_int32
    start_y: c_int32
    size_x: c_int16
    size_y: c_int16
    move_x: c_int8
    move_y: c_int8
    

@decoder.register
class PushPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PUSH
    start_x: c_int32
    start_y: c_int32
    size_x: c_int16
    size_y: c_int16
    move_x: c_int8
    move_y: c_int8
    

@decoder.register
class PingPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PING


@decoder.register
class PongPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PONG


@decoder.register
class StepPacket(BasePacket):
    head: ClassVar[Tuple[c_int8]] = (PKID_STEP, PKID_STEP + 1)
    x: c_int32
    y: c_int32
    on: bool
    
    @classmethod
    def read_from(cls, pr: PacketReader) -> BasePacket:
        with pr.atomic() as r:
            r.seek(r.tell() - 1)
            head = r.read(1)
            x, y = r.read_one(c_int32), r.read_one(c_int32)
            raw_data = head + r.read_since_init()
            return cls(_raw=raw_data, x=x, y=y, on=bool(head[0] & 1))


@decoder.register
class PlaceBlockPlayerPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PLACE_BLOCK_PLAYER
    player_id: c_int8
    x: c_int32
    y: c_int32
    type: c_int8
    char: c_byte
    color: c_uint8
    
    
@decoder.register
class SpawnPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_SPAWN
    player_id: c_int8
    name: str8
    x: c_int32
    y: c_int32
    char: c_byte
    color: c_uint8


@decoder.register
class DespawnPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_DESPAWN
    player_id: c_int8
    

@decoder.register
class DataStartPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_DATA_START
    chunk_type: c_uint8
    chunk_x: c_int32
    chunk_y: c_int32
    data_length: c_int32
    

@decoder.register
class DataChunkPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_DATA
    data: bytes16


@decoder.register
class DataEndPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_DATA_END


@decoder.register
class PlayerNicknamePacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PLAYER_NICKNAME
    player_id: c_int8
    name: str8
    
    
@decoder.register
class KickPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_KICK
    reason: str8
    

@decoder.register
class PVPPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PVP
    enabled: bool
    
    
@decoder.register
class HealthPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_HEALTH
    value: c_int8
    
    
@decoder.register
class OperatorPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_OP
    status: bool42
    
    
@decoder.register
class PlacePushablePlayerPacket(BasePacket):
    head: ClassVar[c_int8] = PKID_PLACE_PUSHABLE_PLAYER
    player_id: c_int8
    target_x: c_int32
    target_y: c_int32
    delta_x: c_int8
    delta_y: c_int8
    char: c_byte
    color: c_uint8


__all__ += decoder.classnames

from typing import ClassVar
from ctypes import c_int8
from py64pixels.packets.utils import *

class BasePacket:
    head: ClassVar[c_int8] = 0x00
    _raw: ClassVar[bytes] = b''
    def __init__(self, _raw, **kwargs):
        self.__dict__.update(kwargs)
        self._raw = _raw
        
    @classmethod
    def read_from(cls, pr: PacketReader) -> "BasePacket":
        with pr.atomic() as r:
            r.seek(r.tell() - 1)
            head = r.read(1)
            attributes = {
                k: r.read_one(t)
                for k, t 
                in cls.__annotations__.items()
                if not hasattr(cls, k)
            }
            raw_data = head + r.read_since_init()
            return cls(_raw=raw_data, **attributes)


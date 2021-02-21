from ctypes import c_int8, c_uint8, c_int16, c_uint16, c_int32, c_uint32
from ctypes import c_float, c_double, c_char
from struct import pack, unpack
from io import BytesIO
from typing import Union, Any, NewType

c_type = type(c_int8)
str8 = NewType('Str_sz8', str)
str16 = NewType('Str_sz16', str)
bytes8 = NewType('Bytes_sz8', bytes)
bytes16 = NewType('Bytes_sz16', bytes)
bool42 = NewType('Bool42', bool)

__all__ = [ 'str8', 'str16', 'bytes8', 'bytes16', 'bool42' ]
__all__ += [ 'PacketReader', 'PacketDecoder' ]

class PacketReader(BytesIO):
    def read_one(self, t: Union[type, c_type]) -> Any:
        if t == str8:
            return self.read_one(bytes8).decode('charmap')
        elif t == str16:
            return self.read_one(bytes16).decode('charmap')
        elif t == bytes8:
            return self.read(self.read_one(c_uint8))
        elif t == bytes16:
            return self.read(self.read_one(c_uint16))
        elif t == bool42:
            return self.read_one(c_uint16) == 42
        elif t == bool:
            return self.read(1)[0] != 0
        elif t == c_int8:
            return unpack('b', self.read(1))[0]
        elif t == c_uint8:
            return unpack('B', self.read(1))[0]
        elif t == c_int16:
            return unpack('!h', self.read(2))[0]
        elif t == c_uint16:
            return unpack('!H', self.read(2))[0]
        elif t == c_int32:
            return unpack('!i', self.read(4))[0]
        elif t == c_uint32:
            return unpack('!I', self.read(4))[0]
        elif t == c_float:
            return unpack('!f', self.read(4))[0]
        elif t == c_double:
            return unpack('!d', self.read(8))[0]
        elif t == c_char:
            return self.read(1)
        else:
            raise TypeError('unable to read %s' % t)
    
    def atomic(self):
        return AtomicPacketReader(self)
    
    @property
    def junk(self):
        _now = self.tell()
        junk = self.read()
        self.seek(_now)
        return junk


class AtomicPacketReader(PacketReader):
    def __init__(self, parent: PacketReader):
        PacketReader.__init__(self, parent.getvalue())
        self.seek(parent.tell())
        self._parent = parent

    def __enter__(self):
        self._begin = self.tell()
        return self

    def __exit__(self, a, b, c):
        self._parent.seek(self.tell())
        
    def read_since_init(self):
        _now = self.tell()
        if _now < self._begin:
            raise IOError('reading backwards is not supported')
        self.seek(self._begin)
        data = self.read(_now - self._begin)
        self.seek(_now)
        return data


class PacketDecoder:
    def __init__(self):
        self.packets_mapping = {}
    
    def register(self, pkt_class):
        self.packets_mapping[pkt_class.head] = pkt_class
        return pkt_class
    
    def read_one(self, pr: PacketReader) -> "BasePacket":
        while True:
            id = pr.read(1)[0]
            if id != 0:
                break
        if id in self.packets_mapping:
            return self.packets_mapping[id].read_from(pr)
        for (head, cls) in self.packets_mapping.items():
            if isinstance(head, tuple) and id in head:
                return cls.read_from(pr)
        else:
            raise ValueError('unknown packet with head %.2x' % id)

    @property
    def classnames(self):
        return [cls.__name__ for cls in self.packets_mapping.values()]

from ctypes import *

def to_ptr(data: bytes | bytearray) -> c_char_p:
	...

def rev16(data: c_char_p, dlen: c_int32) -> None:
	...

def crc32(data: c_char_p, dlen: c_int32) -> c_int32:
	...
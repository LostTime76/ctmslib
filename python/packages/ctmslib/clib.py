from ctypes import *
from pathlib import Path

# Load the library
_lib = CDLL(Path(Path(__file__).parent, 'clib.dll'))

# Load the data operations
rev16 = CFUNCTYPE(None, c_char_p, c_int32)(('rev16', _lib))
crc32 = CFUNCTYPE(c_int32, c_char_p, c_int32)(('crc32', _lib))

def to_ptr(data: bytes | bytearray) -> c_char_p:
	return data if data is isinstance(data, bytes) else (c_char * len(data)).from_buffer(data)
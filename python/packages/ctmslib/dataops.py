from . import clib

def align(value: int, align: int) -> int:
	"""
	Aligns an integer value to a specified alignment

	Args:
		value: The integer value to align
		align: The alignment value

	Returns:
		The integer value aligned to the alignment value
	"""
	if align == 0:
		return value
	elif (rem := (value % align)) == 0:
		return align
	return value + align - rem

def extend_to(data: bytes | bytearray, dlen: int, pad: int = 0xFF) -> bytes | bytearray:
	"""
	Extends a buffer to a specified length. If the length value is less than or equal to the length
	of the buffer, no operation is performed.

	Args:
		data: The buffer to extend
		dlen: The length to extend the buffer to
		pad:  The byte value of the bytes to append to the buffer

	Returns:
		The original buffer is returned
	"""
	print(dlen)
	if (extra := (dlen - len(data))) > 0:
		data.extend((pad & 0xFF).to_bytes() * extra)
	return data

def rev16(data: bytearray) -> bytearray:
	"""
	Reverses the endianness of all the 2 byte words within a bytearray

	Args:
		data: The bytearray containing the data to reverse

	Raises:
		TypeError:       If the input data is not a bytearray
		ArithmeticError: If the len of the data is not aligned to 2 bytes

	Returns:
		The original buffer is returned
	"""
	if not isinstance(data, bytearray):
		raise TypeError('Expected a bytearray.')
	elif ((dlen := len(data)) & 0x1) != 0:
		raise ArithmeticError('The length of the bytearray must be 2 byte aligned.')
	clib.rev16(clib.to_ptr(data), dlen)
	return data

def crc32(data: bytes | bytearray) -> int:
	"""
	Calculates the crc32 of a buffer

	Args:
		data: The buffer containing the data to calculate the crc32 of

	Returns:
		The crc32 calculated from the data within the input buffer
	"""
	return clib.crc32(clib.to_ptr(data), len(data))
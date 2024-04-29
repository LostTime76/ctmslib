import struct
from enum import IntFlag
from pathlib import Path
from typing import Iterator, Self, Type

from . import pathutils

class CoffSectionFlags(IntFlag):
	""" Provides a set of flags to describe the attributes of a section within a TI coff image """

	TEXT : int = 0x20
	""" Indicates the section contains code """

	DATA : int = 0x40
	""" Indicates the section contains initialized data """

	BSS : int = 0x80
	""" Indicates the section contains uninitialized data """

	ALLOC_MASK : int = TEXT | DATA | BSS
	""" The bit mask for indicating if a section exists within target memory """

	@property
	def is_allocated(self) -> bool:
		""" Returns a value indicating if the section exists within target memory """
		return (self.value & self.ALLOC_MASK.value) != 0

class CoffSection:
	""" Provides a class to access a section within a TI coff image """

	ENT_SIZE : int = 48
	""" The size of a section entry in bytes within the image """

	# Instance variables
	_name  : str
	_idx   : int
	_paddr : int
	_vaddr : int
	_daddr : int
	_dlen  : int
	_flags : CoffSectionFlags
	_data  : bytearray

	def __init__(self, name: str, idx: int, ent: tuple[int], data: bytearray, blen: int):
		self._load(name, idx, ent, data, blen)

	@property
	def idx(self) -> int:
		"""	Returns the index of the section """
		return self._idx

	@property
	def name(self) -> str:
		""" Returns the name of the section	"""
		return self._name
	
	@property
	def paddr(self) -> int:
		""" Returns the physical address of the section within target memory """
		return self._paddr
	
	@property
	def vaddr(self) -> int:
		""" Returns the virtual address of the section within target memory """
		return self._vaddr
	
	@property
	def flags(self) -> CoffSectionFlags:
		""" Returns the flags for the section """
		return self._flags
	
	@property
	def daddr(self) -> int:
		""" Returns the address of the section within the image	"""
		return self._daddr
	
	@property
	def dlen(self) -> int:
		""" Returns the length of the section data in bytes within the image """
		return self._dlen
	
	@property
	def data(self) -> memoryview:
		""" Returns a mutable view of the section data within the image	"""
		return self._data[self._daddr:self._daddr+self._dlen]

	def _load(self, name: str, idx: int, ent: tuple[int], data: bytearray, blen: int):
		# Make sure the section name is valid
		if (name is None):
			raise MemoryError(f'The section at index {idx} does not have a valid name.')
		
		# Load the section data
		paddr = ent[2]
		vaddr = ent[3]
		dlen  = ent[4]
		daddr = ent[5]
		flags = CoffSectionFlags(ent[10])

		# Update the length of the data if the section is allocated
		dlen = dlen * blen if flags.is_allocated else dlen

		# Make sure the data within the section is valid
		if ((daddr + dlen) > len(data)):
			raise MemoryError(f'The section at index {idx} does not contain valid data.')
		
		# Initialize the section
		self._name  = name
		self._idx   = idx
		self._paddr = paddr
		self._vaddr = vaddr
		self._flags = flags
		self._daddr = daddr
		self._dlen  = dlen
		self._data  = data

class CoffSectionTable:
	""" Provides a class to access the section table within a TI coff image """

	# Instance variables
	_sects : list[CoffSection]
	_tab   : dict[str, CoffSection]

	def __init__(self, sects: list[CoffSection]):
		self._load(sects)

	def _load(self, sects: list[CoffSection]) -> None:
		tab = { }
		for sect in sects:
			if ((name := sect.name) in tab):
				raise MemoryError(f'The image contains a duplicate section named {name}.')
			tab[name] = sect
		self._sects = sects
		self._tab   = tab

	def __len__(self) -> int:
		return len(self._sects)

	def __getitem__(self, key: int | str):
		return self._sects[key] if isinstance(key, int) else self._tab[key]
	
	def __iter__(self) -> Iterator[CoffSection]:
		return iter(self._sects)
	
class CoffSymbol:
	""" Provides a class to access a symbol within a TI coff image """

	ENT_SIZE : int = 18
	""" The size of a symbol entry in bytes within the image """

class CoffImage:
	""" Provides a class to access and manipulate a TI coff image """

	MAGIC : int = 0x0108
	""" The magic value within the image """

	HDR_ENT_SIZE : int = 50
	""" The size of the header entry in bytes within the image """

	NAME_ENT_SIZE : int = 8
	""" The size of a name entry in bytes within the image """

	# Instance variables
	_tid         : int
	_entry       : int
	_nsects      : int
	_strtab_addr : int
	_blen        : int
	_data        : bytearray
	_sectab      : CoffSectionTable

	# List of architecture byte lengths
	_blens = {0x9D: 2, 0x98: 2}

	def __init__(self, data: bytearray):
		"""
		Constructs a new coff image using the data from a buffer

		Args:
			data: The bytearray comprising the coff image data

		Raises:
			MemoryError: If the format of the coff image is not valid
		"""
		self._load(data)

	def copy_sects(self, addr: int, dst: bytearray | memoryview) -> None:
		"""
		Copies the sections allocated within target memory into a buffer

		Args:
			addr: The address within target memory
			dst:  The buffer to copy the sections into
		"""
		end_addr = addr + len(dst)

		for sect in self.sectab:
			paddr = sect.paddr
			vaddr = sect.vaddr
			dlen  = sect.dlen

			if ((paddr >= addr) and ((paddr + dlen) <= end_addr)):
				dst[paddr-addr:paddr-addr+dlen] = sect.data
			elif ((vaddr >= addr) and ((vaddr + dlen) <= end_addr)):
				dst[vaddr-addr:vaddr-addr+dlen] = sect.data

	@classmethod
	def from_file(cls: Type[Self], fpath: str | Path) -> Self:
		"""
		Creates a new coff image by loading the contents of a file

		Args:
			fpath: The path of the file to load

		Raises:
			MemoryError: If the format of the coff image is not valid

		Returns:
			A new coff image loaded from the file
		"""
		return CoffImage(bytearray(pathutils.str2path(fpath).read_bytes()))
	
	@property
	def target_id(self) -> int:
		"""	Gets the target chipset id of the image	"""
		return self._tid
	
	@property
	def entry(self) -> int:
		"""	Gets entry address of the image within target memory """
		return self._entry
	
	@property
	def sectab(self) -> CoffSectionTable:
		"""
		Returns the section table within the image

		Raises:
			MemoryError: If the format of the image is not valid
		"""
		# Ensure the section table is loaded
		if (self._sectab is None):
			self._sectab = self._load_sect_tab()
		
		# Return the table
		return self._sectab

	def _load(self, data: bytearray) -> None:
		dview = memoryview(data)
		dlen  = len(data)

		# Make sure there is enough data within the buffer to read the header
		if (dlen < self.HDR_ENT_SIZE):
			raise MemoryError('The data does not represent a valid coff image.')
		
		# Unpack the header
		hdr = struct.unpack("<2H3I5H6I", dview[:self.HDR_ENT_SIZE])

		# Load the header
		nsects      = hdr[1]
		symtab_addr = hdr[3]
		nsyms       = hdr[4]
		tid         = hdr[7]
		magic       = hdr[8]
		entry       = hdr[13]

		# Calculate image info
		sectab_end  = self.HDR_ENT_SIZE + nsects * CoffSection.ENT_SIZE
		strtab_addr = symtab_addr + nsyms * CoffSymbol.ENT_SIZE
		strtab_len  = dlen - strtab_addr
		strtab_end  = strtab_addr + strtab_len

		# Make sure the magic value is valid
		if (magic != self.MAGIC):
			raise MemoryError(f'Expected a magic value of {self.MAGIC} within the image \
				but read {magic}.')
		
		# Make sure the target id is valid
		elif (tid == 0):
			raise MemoryError(f'The target chipset for the image is not valid.')
		
		# Make sure the section table is valid
		elif (sectab_end > dlen):
			raise MemoryError('The image does not contain a valid section table.')
		
		# Make sure the symbol table is valid
		elif((sectab_end > symtab_addr) or (strtab_addr > dlen)):
			raise MemoryError('The image does not contain a valid symbol table.')
		
		# Make sure the string table is valid
		elif ((strtab_len <= 0) or (strtab_end > dlen)):
			raise MemoryError('The image does not contain a valid string table.')
		
		# Initialize the image
		self._tid         = tid
		self._nsects      = nsects
		self._entry       = entry
		self._strtab_addr = strtab_addr
		self._data        = data
		self._sectab      = None
		self._blen        = CoffImage._blens[tid] if tid in CoffImage._blens else 1

	def _load_sect_tab(self) -> CoffSectionTable:
		addr  = self.HDR_ENT_SIZE
		data  = memoryview(self._data)
		sects = []
		for idx in range(0, self._nsects):
			ent  = struct.unpack('<12I', data[addr:addr+CoffSection.ENT_SIZE])
			name = self._get_ent_name(data, addr, ent[0] == 0, ent[1])
			addr = addr + CoffSection.ENT_SIZE
			sects.append(CoffSection(name, idx, ent, self._data, self._blen))
		return CoffSectionTable(sects)
	
	def _get_ent_name(self, data: memoryview, addr: int, has_str: bool, str_offs: int) -> str:
		max = self.NAME_ENT_SIZE
		if (has_str):
			addr = self._strtab_addr + str_offs
			max  = len(data) - addr
		return self._get_str(data[addr:addr+max]) if max > 0 else None
		
	def _get_str(self, data: memoryview) -> str:
		slen = 0
		while ((slen < len(data)) and (data[slen] != 0)):
			slen = slen + 1
		return data[:slen].tobytes().decode()
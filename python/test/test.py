import config
import time
from pathlib import Path

from ctmslib import (
	dataops,
	pathutils
)

from ctmslib.coff import (
	CoffImage,
	CoffSectionTable,
	CoffSection,
	CoffSectionFlags
)

fpath = Path(Path(__file__).parent, 'test.out')

coff = CoffImage.from_file(fpath)

t1 = time.time()

b = bytearray([255]) * (0x90000 << 1)

coff.copy_sects(0x80000, b)

dataops.rev16(b)

t2 = time.time()

print(t2 - t1)

Path(Path(__file__).parent, 'tst.bin').write_bytes(b)
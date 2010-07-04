#!/usr/bin/env python
import sys, os.path, struct
debug = False
if debug:
	import pdb, traceback
else:
	try:
		import psyco
		psyco.full()
	except:
		pass

def is_honmon_menu_midashi(ch):
	assert type(ch) == type('')
	assert len(ch) == 1
	return ch in '\x00\x01\x03\x05\x07\x0a'

ctrlcodearglen = {
		'\x09': 2,
		'\x41': 2,
		'\x62': 6,
		'\xe0': 2,
		'\x39': 44,
		'\x4a': 16,
		'\x44': 6,
		'\x64': 6,
		'\x4d': 18,
		'\x63': 6,
		}

assert __name__ == '__main__'

if len(sys.argv) < 4 or len(sys.argv) % 2 == 1:
	print 'Usage: %s honmon_file from_word to_word [from_word to_word...]'%(
			os.path.basename(sys.argv[0],))
	print 'Replace non-ctrl-code-word from_word to any to_word, both in hex'
	print 'Example: %s HONMON FEFE 1F1F' % (os.path.basename(sys.argv[0],))
	sys.exit(0)

subsmap = {}
for i in xrange(2, len(sys.argv), 2):
	from_code = int(sys.argv[i], 16)
	to_code = int(sys.argv[i+1], 16)
	subsmap[struct.pack('!H', from_code)] = struct.pack('!H', to_code)

BLKSIZE = 2048

f = open(sys.argv[1], 'r+b')
mgmtinfo = f.read(BLKSIZE)
numelem = struct.unpack('!H', mgmtinfo[:2])[0]
blktodo = []
for i in xrange(numelem):
	elem = mgmtinfo[16*(i+1):16*(i+2)]
	if not is_honmon_menu_midashi(elem[0]):
		continue
	startblk, numblk = struct.unpack('!LL', elem[2:10])
	blktodo.append((startblk-1, startblk+numblk-1))
print blktodo
for i in xrange(len(blktodo)):
	skipword = 0
	chgedblk = 0
	for blkidx in xrange(blktodo[i][0], blktodo[i][1]):
		f.seek(blkidx * BLKSIZE)
		s = f.read(BLKSIZE)
		assert len(s) == BLKSIZE
		blkchged = False
		j = skipword
		while j < BLKSIZE:
			if s[j] == '\x1f':
				j += 2 + ctrlcodearglen.get(s[j+1], 0)
			else:
				if subsmap.has_key(s[j:j+2]):
					s = s[:j] + subsmap[s[j:j+2]] + s[j+2:]
					blkchged = True
				j += 2
		skipword = j - BLKSIZE
		if blkchged:
			chgedblk += 1
			f.seek(blkidx * BLKSIZE)
			f.write(s)
	print 'Changed %d blockes in [%d, %d]' % (chgedblk, blktodo[i][0]+1,
			blktodo[i][1])
f.close()

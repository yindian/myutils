#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, os.path, struct, os

def showhelp():
	print "Usage: %s somedict.ifo" % os.path.basename(sys.argv[0])
	print "Re-sort Stardict .pos position file"

assert __name__ == '__main__'

if len(sys.argv) != 2:
	showhelp()
	sys.exit(0)

base, ext = os.path.splitext(sys.argv[1])
assert ext == '.ifo'
assert os.path.exists(base + '.ifo')
assert os.path.exists(base + '.idx')
assert os.path.exists(base + '.pos')

print >> sys.stderr, 'Reading...'

f = open(base + '.ifo', 'r')
ifolines = f.readlines()
f.close()
ifodict = dict(map(lambda s: s.split('=', 1), ifolines[1:]))
assert ifodict.has_key('wordcount')
assert not ifodict.has_key('idxoffsetbits')
wordcount = int(ifodict['wordcount'])
idxfilesize = int(ifodict['idxfilesize'])

f = open(base + '.idx', 'rb')
idxcontent = f.read()
assert f.tell() == idxfilesize
f.close()
f = open(base + '.pos', 'rb')
poscontent = f.read()
assert f.tell() == 4 * wordcount
f.close()

poslist = []
for i in xrange(wordcount):
	pos = struct.unpack('<L', poscontent[i*4:(i+1)*4])[0]
	p = idxcontent.find('\x00', pos)
	assert p >= pos
	if p == pos:
		print >> sys.stderr, '%d-th word is empty' % (i,)
	poslist.append((idxcontent[pos:p].decode('latin-1').lower().encode('latin-1'), pos))

print >> sys.stderr, 'Sorting...'

poslist.sort()

print >> sys.stderr, 'Writing...'
f = open(base + '.pos.new', 'wb')
pos = 0
for word, pos in poslist:
	f.write(struct.pack('<L', pos))
f.close()

print >> sys.stderr, 'Done'

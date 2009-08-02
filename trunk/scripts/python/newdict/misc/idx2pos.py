#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, os.path, struct, os

def showhelp():
	print "Usage: %s somedict.ifo" % os.path.basename(sys.argv[0])
	print "Generate .pos file for S60Dict from .idx file"

assert __name__ == '__main__'

if len(sys.argv) != 2:
	showhelp()
	sys.exit(0)

base, ext = os.path.splitext(sys.argv[1])
assert ext == '.ifo'
assert os.path.exists(base + '.ifo')
assert os.path.exists(base + '.idx')

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
reidx = re.compile(r'.*?\x00.{8}', re.S)
idxmatches = reidx.findall(idxcontent)
#print len(idxmatches)
assert len(idxmatches) == wordcount

print >> sys.stderr, 'Writing...'
f = open(base + '.pos', 'wb')
pos = 0
for record in idxmatches:
	p = record.find('\x00')
	if p >= 200:
		print >> sys.stderr, 'Warning: keyword longer than 200 bytes:',
		print >> sys.stderr, record[:p]
	f.write(struct.pack('<L', pos))
	pos += len(record)
f.close()

print >> sys.stderr, 'Done'

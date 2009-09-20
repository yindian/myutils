#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, os.path, struct, os

def showhelp():
	print "Usage: %s somedict.ifo" % os.path.basename(sys.argv[0])
	print "Re-sort Stardict .idx index file"

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
idxlist = []

for record in idxmatches:
	p = record.find('\x00') + 1
	ar = struct.unpack('!%dc2L' % p, record)
	word = ''.join(ar[:-3])
	idxlist.append((unicode(word, 'latin-1').lower().encode('latin-1'),
		word, ar[-2], ar[-1]))
	#try:
	#	print unicode(idxlist[-1][0], 'utf-8').encode('gbk', 'replace'), idxlist[-1][1:]
	#except:
	#	print idxlist[-1]
	#	raise


print >> sys.stderr, 'Generating...'

idxlist.sort()

result = []
for tmp, word, offset, length in idxlist:
	result.append(word)
	result.append('\0')
	result.append(struct.pack('!2L', offset, length))
result = ''.join(result)

print >> sys.stderr, 'Writing...'

f = open(base + '.idx.new', 'wb')
f.write(result)
f.close()

print >> sys.stderr, 'Done'

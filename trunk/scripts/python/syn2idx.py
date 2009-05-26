#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re, os.path, struct, os

def showhelp():
	print "Usage: %s somedict.ifo" % os.path.basename(sys.argv[0])
	print "Merge Stardict synonym file (.syn) into .idx"

assert __name__ == '__main__'

if len(sys.argv) != 2:
	showhelp()
	sys.exit(0)

base, ext = os.path.splitext(sys.argv[1])
assert ext == '.ifo'
assert os.path.exists(base + '.ifo')
assert os.path.exists(base + '.idx')
assert os.path.exists(base + '.syn')

print >> sys.stderr, 'Reading...'

f = open(base + '.ifo', 'r')
ifolines = f.readlines()
f.close()
ifodict = dict(map(lambda s: s.split('=', 1), ifolines[1:]))
assert ifodict.has_key('synwordcount')
assert ifodict.has_key('wordcount')
assert not ifodict.has_key('idxoffsetbits')
wordcount = int(ifodict['wordcount'])
synwordcount = int(ifodict['synwordcount'])
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
	idxlist.append((word, ar[-2], ar[-1]))
	#try:
	#	print unicode(idxlist[-1][0], 'utf-8').encode('gbk', 'replace'), idxlist[-1][1:]
	#except:
	#	print idxlist[-1]
	#	raise

f = open(base + '.syn', 'rb')
syncontent = f.read()
f.close()
resyn = re.compile(r'.*?\x00.{4}', re.S)
synmatches = resyn.findall(syncontent)
#print len(synmatches)
assert len(synmatches) == synwordcount
synlist = []

for record in synmatches:
	p = record.find('\x00') + 1
	ar = struct.unpack('!%dcL' % p, record)
	word = ''.join(ar[:-2])
	synlist.append((word, ar[-1]))
	#try:
	#	print unicode(synlist[-1][0], 'utf-8').encode('gbk', 'replace'), synlist[-1][1]
	#except:
	#	print synlist[-1]
	#	raise

print >> sys.stderr, 'Generating...'

for synword, index in synlist:
	idxlist.append((synword, idxlist[index][1], idxlist[index][2]))

idxlist.sort()

result = []
for word, offset, length in idxlist:
	result.append(word)
	result.append('\0')
	result.append(struct.pack('!2L', offset, length))
result = ''.join(result)

for i in range(len(ifolines)):
	if ifolines[i].startswith('wordcount'):
		assert len(idxlist) == wordcount + synwordcount
		ifolines[i] = 'wordcount=%d\n' % len(idxlist)
	elif ifolines[i].startswith('synwordcount'): 
		ifolines[i] = ''
	elif ifolines[i].startswith('idxfilesize'): 
		ifolines[i] = 'idxfilesize=%d\n' % len(result)

print >> sys.stderr, 'Writing...'

os.remove(base + '.syn')
f = open(base + '.idx', 'wb')
f.write(result)
f.close()
f = open(base + '.ifo', 'wb')
f.writelines(ifolines)
f.close()

print >> sys.stderr, 'Done'

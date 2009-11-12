#!/usr/bin/env python
myencoding = 'gbk'
import sys
try:
	import psyco
	psyco.full()
except:
	print >> sys.stderr, 'Warning: psyco not installed.'
	pass

gb2312uni = []
f = open('GB2312.TXT', 'r')
for line in f:
	if line[0] == '#':
		continue
	ar = line[:line.find('#')].lstrip().split()
	assert len(ar) == 2
	gb2312uni.append([int(x, 0) for x in ar])
f.close()

gb12345uni = []
f = open('GB12345.TXT', 'r')
for line in f:
	if line[0] == '#':
		continue
	ar = line[:line.find('#')].lstrip().split()
	assert len(ar) == 2
	gb12345uni.append([int(x, 0) for x in ar])
f.close()

exclusion = set([])
try:
	f = open('exclusion.lst', 'r')
	for line in f:
		exclusion.add(int(line, 0))
	f.close()
except IOError:
	pass

gb2312unimap = dict(gb2312uni)
gb12345unimap = dict(gb12345uni)

#unigb2312map = dict([(b, a) for (a, b) in gb2312uni])
#unigb12345map = dict([(b, a) for (a, b) in gb12345uni])

oneonemap23to12 = []

for gb, uni in gb2312uni:
	assert gb12345unimap.has_key(gb)
	if gb12345unimap[gb] == uni: continue
	if uni in exclusion: continue
	oneonemap23to12.append((uni, gb12345unimap[gb]))

oneonemap12to23 = dict([(b, a) for (a, b) in oneonemap23to12])
oneonemap23to12 = dict(oneonemap23to12)

if __name__ == '__main__':
	oneonemap = oneonemap12to23
	if len(sys.argv) >= 2:
		if sys.argv[1] == '-r':
			oneonemap = oneonemap23to12
	if len(sys.argv) >= 2 and sys.argv[-1] != '-r':
		myencoding = sys.argv[-1]
	for line in sys.stdin:
		line = unicode(line, myencoding)
		line = ''.join(map(unichr, [oneonemap.get(ch, ch) for ch in 
			map(ord, line)]))
		sys.stdout.write(line.encode(myencoding))

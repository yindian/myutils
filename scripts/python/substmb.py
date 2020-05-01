#!/usr/bin/env python
import sys
from collections import OrderedDict
import pdb

assert __name__ == '__main__'

with open(sys.argv[1], 'rb') as f:
	buf = f.read().decode('utf-16le')
if buf.startswith(u'\ufeff'):
	buf = buf[1:]
try:
	mb = map(unicode.split, buf.splitlines())
except NameError:
	mb = list(map(str.split, buf.splitlines()))
d = OrderedDict(mb)
mb = [(b, a) for a, b in mb]
dd = OrderedDict(mb)

nsame = ndiff = nnew = 0
cs = set()

with open(sys.argv[2], 'rb') as f:
	buf = f.read().decode('utf-8')
lines = buf.splitlines()
for line in lines:
	ar = line.split(',')
	if ar[2]:
		assert ar[1]
		c = ar[1]
		k = ar[2]
		if c in d:
			#br = [x for x in mb if x[1] == c]
			#if len(br) != 1:
			#	print(c, br)
			#	pdb.set_trace()
			if d[c] != k:
				#print((u'Key for %s differ: %s => %s' % (
				#	c, d[c], k)))
				cs.add(c)
				ndiff += 1
			else:
				nsame += 1
		else:
			#print((u'New key for %s: %s' % (
			#	c, k)))
			nnew += 1
#print('%d same, %d diff, %d new' % (nsame, ndiff, nnew))

mb = [x for x in mb if x[1] not in cs]
for line in lines:
	ar = line.split(',')
	if ar[2]:
		assert ar[1]
		c = ar[1]
		k = ar[2]
		if c in d:
			if d[c] != k:
				mb.append((k, c))
		else:
			mb.append((k, c))
mb.sort(key=lambda x: x[0])
#buf = u'\n'.join(map(u'\t'.join, mb))
dd = {}
for k, c in mb:
	dd.setdefault(k, []).append(c)
buf = u'\n'.join(map(u'\t'.join, [(k, u','.join(c)) for k, c in sorted(dd.items())]))
try:
	print(buf)
except UnicodeEncodeError:
	print(buf.encode('utf-8'))

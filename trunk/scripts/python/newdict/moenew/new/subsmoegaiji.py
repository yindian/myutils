#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import psyco
	psyco.full()
except:
	pass
import sys
gaijimap = {}
f = open('gaiji.txt', 'r')
for line in f:
	line = line[:-1].split()
	assert len(line) == 4
	src = int(line[2], 16)
	dest = line[-1]
	if dest.find('#') >= 0:
		dest = dest[:dest.find('#')]
	assert src and not gaijimap.has_key(src)
	try:
		assert dest and dest.count('|') <= 1
		if dest[0] == '{':
			assert dest[-1] == '}' and dest.count('{') == dest.count('}') == 1
	except:
		print >> sys.stderr, hex(src), unicode(dest, 'utf-8').encode('gbk', 'replace')
		raise
	gaijimap[src] = unicode(dest, 'utf-8')
f.close()

def fwalpha2hw(str):
	result = []
	for c in str:
		if 0xFF21 <= ord(c) <= 0xFF3A or 0xFF41 <= ord(c) <= 0xFF5A:
			result.append(unichr(ord(c) - 0xFF00 + 0x20))
		else:
			result.append(c)
	return u''.join(result)

def subsgaiji(str):
	result = []
	for c in str:
		result.append(gaijimap.get(ord(c), c))
	return u''.join(result)

def substitlegaiji(str):
	result1 = []
	result2 = []
	for c in str:
		try:
			dest = gaijimap[ord(c)]
		except KeyError:
			result1.append(c)
			result2.append(c)
			continue
		if dest[0] == u'{':
			p = dest.find(u'|')
			if p < 0:
				assert len(dest) > 3
				result1.append(dest)
				result2.append(dest)
			else:
				result1.append(dest[1:p])
				other = dest[p+1:-1]
				p = other.find(u'?')
				assert p != 0
				if p > 0:
					other = other[:p]
				if len(other) <= 1:
					assert other
					result2.append(other)
				else:
					result2.append(u'{')
					result2.append(other)
					result2.append(u'}')
		else:
			result1.append(dest)
			result2.append(dest)
	result1 = u''.join(result1)
	result2 = u''.join(result2)
	if result1 == result2:
		return result1
	else:
		return u'|'.join([result1, result2])

for line in sys.stdin:
	line = unicode(line[:-1], 'utf-8')
	word, mean = line.split(u'\t')
	try:
		word = substitlegaiji(word)
	except:
		print >> sys.stderr, word.encode('gbk', 'replace')
		raise
	means = mean.split(u'\\n')
	for i in range(len(means)):
		means[i] = fwalpha2hw(subsgaiji(means[i]))
	mean = u'\\n'.join(means)
	print (word + u'\t' + mean).encode('utf-8')

#!/usr/bin/env python
import sys, os.path

def isuro(ch):
	return len(ch) == 1 and 0x4E00 <= ord(ch) <= 0x9FA5

assert __name__ == '__main__'
if len(sys.argv) < 3:
	print 'Usage: %s map.txt tabfile.txt' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

d = {}
f = open(sys.argv[1], 'r')
lineno = 0
for line in f:
	lineno += 1
	if not line.strip(): continue
	try:
		line = line.rstrip().split('\t')
		assert line[0].startswith('U+')
		ch = unichr(int(line[0][2:], 16))
		br = line[2].decode('utf-8').split(u'|')
		if line[1].find('**') >= 0:
			assert line[1] == '**'
			assert len(br) == 2
			if ch == br[0] and isuro(br[1]):
				d[ch] = ([br[1]], br[1])
			elif ch == br[1] and isuro(br[0]): 
				d[ch] = ([br[0]], br[0])
			else:
				assert (ch == br[0] and isuro(br[1])) or (
						ch == br[1] and isuro(br[0]))
		else:
			ar = line[1].decode('utf-8').split('*')
			if not ar[0]:
				assert len(ar) == 2
				assert ar[1]
				d[ch] = ([ar[1]], ar[1])
			elif len(ar) == 1:
				d[ch] = ([ar[0]], ar[0])
			else:
				bodymap = ar[0]
				assert len(ar) == 2
				for c in ar:
					if isuro(c) or c.startswith(u'{'):
						bodymap = c
						break
				if bodymap[0] == u'{':
					assert bodymap[-1] == u'}'
					for c in bodymap[1:-1]:
						assert isuro(c) or c in '@/()'
				d[ch] = (ar, bodymap)
	except:
		print 'Error on %s:%d' % (sys.argv[1], lineno)
		raise
f.close()

def keymap(key, d=d):
	p = -1
	for i in xrange(len(key)):
		if d.has_key(key[i]):
			p = i
			break
	if p < 0:
		return key
	else:
		result = []
		head = key[:p]
		tail = keymap(key[p+1:], d).split(u'|')
		for c in d[key[p]][0]:
			for i in xrange(len(tail)):
				result.append(head + c + tail[i])
		return u'|'.join(result)

bodyfirstlinemap = lambda c: d.get(c, [[c]])[0][0]
bodymap = lambda c: d.get(c, [None, c])[1]

f = open(sys.argv[2], 'r')
for line in f:
	assert line.endswith('\n')
	line = line[:-1].decode('utf-8').replace(u'\u0115', u'\u011b').replace(u'\u301c', u'\uff5e').replace(u'\u2212', u'\uff0d')
	word, mean = line.split(u'\t', 1)
	result = u'|'.join(map(keymap, word.split(u'|'))).split(u'|')
	more = True
	while more:
		more = False
		for i in xrange(len(result)-1, 0, -1):
			if result[i] in result[:i]:
				del result[i]
				more = True
				break
	result = [u'|'.join(result), u'\t']
	p = mean.find(u'\\n')
	assert p <= 0 or mean[p-1] != u'\\'
	result.extend(map(bodyfirstlinemap, mean[:p]))
	result.extend(map(bodymap, mean[p:]))
	print u''.join(result).encode('utf-8')
f.close()

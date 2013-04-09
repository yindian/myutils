#!/usr/bin/env python
import sys, os.path
import re

charrefpat = re.compile(r'&#(\d+);')
charrefsub = lambda m: unichr(int(m.group(1))).encode('utf-8')
charxrefpat = re.compile(r'&#x([0-9A-Fa-f]+);')
charxrefsub = lambda m: unichr(int(m.group(1), 16)).encode('utf-8')
nobrpat = re.compile(r'</?NOBR>')
imgpat = re.compile(r'<img [^>]*>')
tagpat = re.compile(r'<[^>]*>')
subentrystart = '<BR>&nbsp;<BR><span class="wb-dict-headword">'
subentryend = '</span>'

headwordpat = re.compile(r'<span class="wb-dict-headword">(.*?)</span>')
bpat = re.compile(r'</?B>(.*?)</?B>')
def find_words(buf, oldwords=None):
	words = headwordpat.findall(buf)
	if not words:
		return words
	words = [words[0]] + sorted(list(set(words).difference(set([words[0]]))))
	if ('<B>a</B>' in words or '<B>1</B>' in words) and (oldwords and len(oldwords[0]) > 1 or len(''.join(bpat.findall(words[0]))) > 1):
		if '<B>a</B>' in words:
			if len(''.join(bpat.findall(words[0]))) == 1:
				s = set(words)
			else:
				s = set(words).difference(set([words[0]]))
			c = 'a'
			while '<B>%s</B>' % (c,) in s:
				s.remove('<B>%s</B>' % (c,))
				c = chr(ord(c) + 1)
			if len(''.join(bpat.findall(words[0]))) == 1:
				words = sorted(list(s))
			else:
				words = [words[0]] + sorted(list(s))
		if '<B>1</B>' in words:
			if len(''.join(bpat.findall(words[0]))) == 1:
				s = set(words)
			else:
				s = set(words).difference(set([words[0]]))
			c = '1'
			while '<B>%s</B>' % (c,) in s:
				s.remove('<B>%s</B>' % (c,))
				c = chr(ord(c) + 1)
			if len(''.join(bpat.findall(words[0]))) == 1:
				words = sorted(list(s))
			else:
				words = [words[0]] + sorted(list(s))
	words = [''.join(bpat.findall(s)).replace('\\n', '') for s in words]
	words = [tagpat.sub('', s) for s in filter(lambda s: not imgpat.search(s), words)]
	return words

entrystart = '<A NAME="ent_'
def remove_duplicate_entry(mean, words=None, visited=set([])):
	ar = mean.split(entrystart)
	result = [ar[0]]
	newwords = find_words(ar[0], words)
	delwords = []
	for s in ar[1:]:
		p = s.index('">')
		now = int(s[:p])
		nowwords = find_words(s, words)
		if now in visited:
			print >> sys.stderr, 'Remove duplicate entries', nowwords, 'in', words
			delwords.extend(nowwords)
			continue
		visited.add(now)
		result.append(entrystart)
		result.append(s)
		newwords.extend(nowwords)
	try:
		newwords = [newwords[0]] + sorted(list(set(newwords).difference(set([newwords[0]]))))
		#assert set(newwords).isdisjoint(set(delwords))
		assert set(newwords).union(set(delwords)) == set(words)
	except:
		print >> sys.stderr, 'New words:', newwords, 'Removed words:', delwords, 'Old words:', words
	if words and set(words) != set(newwords):
		words[:] = newwords[:]
	return ''.join(result).rstrip('\\n')

entrysep = '<br><hr size="1" width="100"><br>'

assert __name__ == '__main__'

f = open(sys.argv[1])

for line in f:
	words, mean = line.rstrip().split('\t', 1)
	words = [tagpat.sub('', s) for s in filter(lambda s: not imgpat.search(s), words.split('|'))]
	mean = charxrefpat.sub(charxrefsub, charrefpat.sub(charrefsub, mean)).replace('"bword:// ', '"bword://')
	try:
		mean = remove_duplicate_entry(mean, words)
	except:
		print >> sys.stderr, 'Error processing', words
		raise
	if mean.find(entrystart) < 0:
		#print >> sys.stderr, 'Ignoring empty entry', words
		pass
	else:
		assert mean.endswith(entrysep)
		mean = mean[:-len(entrysep)]
		print '%s\t%s' % ('|'.join(words), mean)
	p = mean.find(subentrystart)
	while p > 0:
		q = mean.index(subentryend, p + len(subentrystart))
		p = mean.find(subentrystart, q + len(subentryend))

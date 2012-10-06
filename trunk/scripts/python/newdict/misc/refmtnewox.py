#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
soloparenpat = re.compile(r'\(([^()]*)$')

def reindent(mean):
	ar = mean.split('\\n')
	result = [ar[0]]
	if len(ar) > 1:
		result.append('\\n')
	for s in ar[1:]:
		if result[-2] and s and not s.startswith('<') and (result[-2].startswith('*') or result[-2].startswith('■')):
			result.append('  ')
		result.append(s)
		result.append('\\n')
	del result[-1]
	return ''.join(result)

def unblock(mean):
	ar = mean.split('<blockquote>')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index('</blockquote>')
		result.append('<ex>')
		for t in s[:p].split('\\n'):
			result.append(' 　')
			result.append(t)
			result.append('\\n')
		del result[-1]
		result.append('</ex>')
		result.append(s[p+13:])
	return ''.join(result)

ampunquote=lambda s:s.replace('&quot;', '"').replace('&apos;', "'").replace(
		'&gt;'  , '>').replace('&lt;'  , '<').replace('&amp;' , '&')
def titlefmt(word):
	return soloparenpat.sub('', word)
phsec = set('''\
习惯用语
继承用法
常用词组
'''.splitlines())
def phraseit(origword, mean, phrase):
	ar = mean.split('\\n')
	state = 0
	result = []
	section = None
	word = mean = None
	for i in xrange(len(ar)):
		s = ar[i]
		if state == 0:
			if s.startswith('<c c="blue"><b>'):
				assert s.endswith('</b></c>')
				state = 1
				section = s[15:-8]
		elif state == 1:
			if section in phsec and s.startswith('<b>'):
				assert s.endswith('</b>')
				word = s[3:-4]
				mean = ['<k>%s</k>' % (word,), ' &lt;= <kref>%s</kref>' % (origword,)]
				word = ampunquote(word)
				state = 2
			elif not s:
				state = 0
			else:
				assert not s.startswith('<c')
		elif state == 2:
			if not s:
				phrase.append((word, '\\n'.join(mean)))
				word = mean = None
				state = 0
			elif s.startswith('<b>'):
				phrase.append((word, '\\n'.join(mean)))
				assert s.endswith('</b>')
				word = s[3:-4]
				mean = ['<k>%s</k>' % (word,), ' &lt;= <kref>%s</kref>' % (origword,)]
				word = ampunquote(word)
			else:
				try:
					assert s.startswith('<ex>') or s.startswith('<tr>') or not s.startswith('<')
				except:
					print >> sys.stderr, s
					raise
				mean.append(s)
	if word:
		phrase.append((word, '\\n'.join(mean)))
	return '\\n'.join(ar)

import sys
f = open(sys.argv[1])
for line in f:
	word, mean = line.rstrip('\n').split('\t')
	syn = word.split('|')
	phrase = []
	mean = phraseit(syn[0], unblock(reindent(mean)), phrase)
	if phrase:
		s = []
		for i in xrange(len(phrase)):
			s.append(phrase[i][0])
		s = set(s)
		i = 0
		while i < len(syn):
			if syn[i] in s:
				del syn[i]
			else:
				i += 1
	print '%s\t%s' % ('|'.join(syn), mean)
	if phrase:
		for word, mean in phrase:
			print '%s\t%s' % (titlefmt(word), mean)
f.close()

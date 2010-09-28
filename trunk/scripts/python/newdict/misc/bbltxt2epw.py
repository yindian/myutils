#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os, string
import pprint, pdb

def enc(str):
	return str.encode('sjis', 'xmlcharrefreplace')

supmap = {
u'\u2070':	'0',
u'\u2071':	'l',
u'\u00B9':	'1',
u'\u00B2':	'2',
u'\u00B3':	'3',
u'\u2074':	'4',
u'\u2075':	'5',
u'\u2076':	'6',
u'\u2077':	'7',
u'\u2078':	'8',
u'\u2079':	'9',
u'\u207a':	'+',
u'\u207b':	'-',
u'\u207c':	'=',
u'\u207d':	'(',
u'\u207e':	')',
u'\u207f':	'n',
}
submap = {
u'\u2080':	'0',
u'\u2081':	'1',
u'\u2082':	'2',
u'\u2083':	'3',
u'\u2084':	'4',
u'\u2085':	'5',
u'\u2086':	'6',
u'\u2087':	'7',
u'\u2088':	'8',
u'\u2089':	'9',
u'\u208a':	'+',
u'\u208b':	'-',
u'\u208c':	'=',
u'\u208d':	'(',
u'\u208e':	')',
}
def supsub(str):
	result = []
	for c in str:
		if supmap.has_key(c):
			result.append('<sup>%s</sup>'% supmap[c])
		elif submap.has_key(c):
			result.append('<sub>%s</sub>'% submap[c])
		else:
			result.append(c)
	return ''.join(result)

def filterwords(words):
	if words[0].isdigit():
		del words[0]
	for i in xrange(len(words)):
		words[i] = words[i].replace('//', '')
	return words

def showwords(words):
	p = 0
	if ord(words[0][0]) > 0x3000:
		p += 1
	return '<p>%s</p>' % (enc(words[p]),)

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s babylon_src_txt' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
<title>Untitled</title>
</head>
<body>"""

f = open(sys.argv[1], 'r')
state = 0
for line in f:
	line = line.rstrip().decode('utf-8')
	if state == 0:
		words = filter(None, map(string.strip, line.split('|')))
		words = filterwords(words)
		assert words[0]
		print '<dl>\n<dt>【%s】</dt>' % (enc(words[0]),)
		for alt in words[1:]:
			print '<key type="表記">%s</key>' % (enc(alt),)
		print '<dd>'
		s = showwords(words)
		if s: print s
		state = 1
	elif state == 1:
		if not line:
			print '</dd>\n</dl>'
			state = 0
		else:
			line = line.replace('\x1e', '').replace('\x1f', '')
			line = line.replace('.gif', '.bmp')
			line = supsub(line)
			print enc(line)
f.close()

print """\
</body>
</html>"""

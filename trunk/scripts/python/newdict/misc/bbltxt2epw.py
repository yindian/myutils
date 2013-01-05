#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os, string, re
import unicodedata
import pprint, pdb

try:
	import tcscconv
except ImportError:
	totrad = lambda s: s
else:
	c = tcscconv.TCSCconv()
	totrad = c.toTrad

import codecs
from htmlentitydefs import codepoint2name
def html_replace(exc):
	assert isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError))
	s = [ u'&%s;' % codepoint2name.get(ord(c), '#x%04X' % (ord(c),))
			for c in exc.object[exc.start:exc.end] ]
	return ''.join(s), exc.end
codecs.register_error('html_replace', html_replace)

def enc(str, err='html_replace'):
	return str.encode('sjis', err)

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
	return enc(' '.join(words[p:-1]))

def half(s):
	result = []
	for c in s:
		cc = ord(c)
		if 0xFF00 <= cc < 0xFF5F:
			result.append(chr(cc - 0xFEE0))
		else:
			result.append(c)
	return u''.join(result)

def idenc(word, pron):
	return half(word + pron.lower().replace(' ', '').replace('/', '')).encode('utf-8').encode('base64').replace('\n', '')

colorful = re.compile(r'<FONT COLOR=#D23636>(.*?)</FONT>')
wordheadpat = re.compile(ur"<FONT FACE='ＭＳ Ｐ明朝' COLOR=#AAAAAA SIZE=\+2>【</FONT><FONT FACE='ＭＳ Ｐ明朝' COLOR=#434343 SIZE=\+2>[^<]*</FONT><FONT FACE='ＭＳ Ｐ明朝' COLOR=#AAAAAA SIZE=\+2>】</FONT>")
charheadpat = re.compile(ur"<FONT FACE='ＭＳ Ｐ明朝' COLOR=#434343 SIZE=\+2>[^<]*</FONT>")
linkpat = re.compile(ur'<FONT COLOR=#D23636>(\u261e)</FONT>([^<]*) <span style="font-family: Tahoma;">([^<]*)</span>')
linkpat2 = re.compile(ur'(\u21d2)([^<]*) <span style="font-family: Tahoma;">([^<]*)</span>')
def linksub(m):
	sign = m.group(1)
	word = m.group(2)
	pron = m.group(3)
	return u'<a href="#%s">%s %s %s</a>' % (idenc(word, pron), sign, word, pron)
def filterline(line):
	line = line.replace('<br>', '')
	line = line.replace('<IMG BORDER="0" HSPACE="0" VSPACE="0" ALIGN="ABSMIDDLE" ALT="" TITLE="" SRC="FE9CED09.bmp">', u'[同]')
	line = line.replace('<IMG BORDER="0" HSPACE="0" VSPACE="0" ALIGN="ABSMIDDLE" ALT="" TITLE="" SRC="7E7DDB96.bmp">', u'[反]')
	line = line.replace('<B>', '').replace('</B>', '')
	line = linkpat.sub(linksub, line)
	line = linkpat2.sub(linksub, line)
	line = colorful.sub(r'<EM>\1</EM>', line)
	line = wordheadpat.sub('', line)
	line = charheadpat.sub('', line)
	line = line.replace('<BR><BR>', '<BR>')
	return line
ctrlpat = re.compile(r'[-]')

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

f = open(sys.argv[1], 'rb')
state = 0
lineno = 0
for line in f:
	lineno += 1
	try:
		line = line.rstrip().decode('utf-8')
		if state == 0:
			words = filter(None, map(string.strip, line.split('|')))
			words = filterwords(words)
			assert words[0]
			print '<dl>\n<dt id="%s">【%s】</dt>' % (idenc(words[0], len(words) > 1 and words[1] or ''), enc(words[0]),)
			alt = totrad(words[0])
			if alt != words[0]:
				print '<key type="表記">%s</key>' % (enc(alt),)
			for alt in words[1:]:
				alt2 = unicodedata.normalize('NFD', alt)
				if alt2 != alt:
					print '<key type="表記">%s</key>' % (enc(alt2, 'ignore'),)
				print '<key type="表記">%s</key>' % (enc(alt),)
			print '<dd>'
			s = showwords(words)
			#if s: print '<p>%s</p>' % (s,)
			state = 1
		elif state == 1:
			if not line:
				print '</dd>\n</dl>'
				state = 0
			else:
				line = line.replace('\x1e', '').replace('\x1f', '')
				line = line.replace('.gif', '.bmp')
				line = supsub(line)
				line = filterline(line)
				line = filter(None, ctrlpat.split(line))
				assert len(line) <= 2
				if len(line) > 1:
					assert line[-1].strip()
					line[0] = line[0].rstrip('(')
					print '<p>%s</p>' % (enc(line[-1]),)
				else:
					print '<p></p>'
				print enc(line[0])
	except:
		print >> sys.stderr, 'Error processing line', lineno
		print >> sys.stderr, len(line), repr(line)[:400]
		raise
f.close()

print """\
</body>
</html>"""

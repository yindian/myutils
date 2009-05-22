#!/usr/bin/env python
# -*- coding: cp936 -*-
import sys, glob, re

# ex commands for vim
# 1s/^\_.\{-}<span class=.\=title_page[^>]*>\([^<]*\)\_.\{-}span class="style27">\(<!--HTMLBUILERPART0-->\)\=/>>\1>/
# %s/^.*HTMLBUILERPART0\_.*//
# %s+<a name[^>]*>\s*</a>++g
# %s+<a href[^>]*><font[^>]*>\s*\(.\{-}\)\s*</font></a>+{\1}+g
# %s+<span style[^>]*>\s*◆\s*</span>\s*+◆+g
# %s/<br>//g
# %s/<p>/>/
# %s/<\/p>//
# %s/　\+$//
# %s/^　*>　*/>/
# %s/\s\+$//
# %s/^\n//
# %s/\n$//

regex = [
		(re.compile(r'^.*?class=.?title_page[^>]*>([^<]*).*?class=.?style27.?>(<!--HTMLBUILERPART0-->)?', re.S), r'>>\1\n>'),
		(re.compile(r'<!--/HTMLBUILERPART0.*', re.S), r''),
		(re.compile(r'<a\s*name[^>]*>\s*</a>', re.I), r''),
		(re.compile(r'<a\s*(?:href|style)[^>]*><font[^>]*>\s*(.*?)\s*</font></a>', re.I), r'\1'), #r'{\1}'
		(re.compile(r'<span\s*style[^>]*>\s*◆\s*</span>\s*', re.I), r'\n◆'),
		(re.compile(r'<p>', re.I), r'\n>'),
		(re.compile(r'<br>', re.I), r'\n'),
		(re.compile(r'<[^>]*>'), r''),
		(re.compile(r'(\t| |　)+$', re.M), r''),
		(re.compile(r'^(\t| |　)*>(\t| |　)*', re.M), r'>'),
		(re.compile(r'^>【(.*)】', re.M), r'>\1'),
		(re.compile(r'^( |\t)*　', re.M), r''),
		(re.compile(r'^>?\n', re.M), r''),
		(re.compile(r'\n$'), r''),
]

assert __name__ == '__main__'

for fname in glob.glob('test*.htm'):
	buf = open(fname, 'r').read()
	for ex, to in regex:
		buf, num = ex.subn(to, buf)
		try:
			assert num >= 1
		except:
			print 'Unexpected:', ex.pattern, to
			print buf
			raise
	assert buf.startswith('>>')
	p = buf.index('\n')
	title = buf[2:p]
	words = buf[p+1:].split('>')
	for one in words[1:]:
		lines = one.splitlines()
		sys.stdout.write(lines[0])
		sys.stdout.write('\t')
		sys.stdout.write(title)
		sys.stdout.write('\\n')
		sys.stdout.write('\\n'.join(lines[1:]))
		sys.stdout.write('\n')

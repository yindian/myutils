#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os, re
from htmlentitydefs import name2codepoint
import pdb

pat = re.compile(r'<dt[^>]*>【(.*)】</dt>')
pat2 = re.compile(r'<key type="(.*?)">(.*?)</key>')

def charref2uni(str):
	ar = str.split('&');
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s.startswith('#x'):
			result.append('%04X' % (int(s[2:p], 16),))
		elif s.startswith('#'):
			result.append('%04X' % (int(s[1:p]),))
		else:
			result.append('%04X' % (name2codepoint[s[:p]],))
		result.append(s[p+1:])
	return ''.join(result)

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s epw_src_htm' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'r')
for line in f:
	sys.stdout.write(line)
	ar = pat.findall(line)
	if ar:
		assert len(ar) == 1
		s = charref2uni(ar[0])
		if s != ar[0]:
			print '<key type="表記">%s</key>' % (s,)
	ar = pat2.findall(line)
	if ar:
		for t, k in ar:
			s = charref2uni(k)
			if s != k:
				print '<key type="%s">%s</key>' % (t, s)
f.close()

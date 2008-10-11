#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, re

def uncode(str):
	b = 168
	r = []
	for c in str:
		o = ord(c)^b
		if o < 0x10000:
			r.append(unichr(o))
		else:
			r.append(u'?')
		b += 8
	return u''.join(r)

l = sys.argv[1:]
n = []
for i in range(len(l)):
	if l[i].startswith('@'):
		map(n.append, open(l[i][1:], 'r').read().splitlines())
	else:
		n.append(l[i])
l = n

for name in l:
	f = open(name, 'rb')
	s = f.read()
	try:
		i = s.index('getUncodePin')
		j = s.index("'", i)
		s = s[j+1 : s.index("'", j+1)]
		s = s.replace('%u', r'\u').replace('%', r'\x')
		us = eval("u'%s'" % (s))
		s = uncode(us).encode('gbk', 'replace')
		p = re.compile(r'''<\s*img[^>]*src\s*=\s*["']([^"']*)["']''', re.I)
		r = p.findall(s)
		sys.stderr.write('.')
		print '\n'.join(r)
	except:
		print >> sys.stderr, "Error processing %s" % (name)
		print "Error occured. Following is s"
		print s
		sys.stdout.flush()
		raise
	f.close()

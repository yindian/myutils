#!/usr/bin/env python
import sys

assert __name__ == '__main__'
assert len(sys.argv) == 2
d = {}
s = set()
ss = set()
sss = set()
f = open(sys.argv[1], 'r')
for line in f:
	first = key = True
	for c in line.decode('utf-8'):
		if first and c == u'|':
			first = False
		elif key and c == u'\t':
			first = key = False
		elif 0xE000 <= ord(c) < 0xF900 and not d.has_key(c):
			d[c] = line[:49][:-1].decode('utf-8', 'ignore').encode('utf-8')
			if first:
				s.add(c)
			elif key:
				ss.add(c)
			else:
				sss.add(c)
f.close()

print '''\
<html>
<head>
    <META http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
<font size=7>'''
order = sorted(list(s)) + [0] + sorted(list(ss)) + [0] + sorted(list(sss))
for k in order:
	if k == 0:
		print '<hr>'
		continue
	v = d[k]
	k = ord(k)
	print 'U+%04X <img src="image/%04x.png"/> X - %s<p>' % (k, k, v)
print '''\
</font>
</body>
</html>'''

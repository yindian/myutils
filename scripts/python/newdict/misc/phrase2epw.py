#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, re
import pdb

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s data_file' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

tagpat = re.compile(r'<[^>]*>')
xpat = re.compile(r'<X4081>(..)(..)</X4081>', re.I)
def tofull(s):
	result = []
	for c in s:
		if ord(c) == 0x20:
			result.append(u'\u3000')
		elif 0x20 < ord(c) < 0x7f:
			result.append(unichr(ord(c) + 0xfee0))
		else:
			result.append(c)
	return ''.join(result)
def enc(s):
	s = s.encode('sjis', 'xmlcharrefreplace')
	ar = s.split('&#')
	result = [ar[0]]
	for s in ar[1:]:
		try:
			p = s.index(';')
			if s[0] == 'x':
				code = int(s[1:p], 16)
			else:
				code = int(s[:p])
			assert not 0xe000 <= code < 0xf900
			s = '<X4081>1F0B</X4081>%s<X4081>1F0C</X4081>%s' % (tofull('%04X' % (code,)).encode('sjis'), s[p+1:])
		except:
			result.append('&#')
		finally:
			result.append(s)
	return ''.join(result)
def enc2title(s):
	s = xpat.sub(r'&#x\g<1>;&#x\g<2>;', s)
	ar = s.split('&#x');
	result = [ar[0]]
	for s in ar[1:]:
		if result[-1] and ord(result[-1].decode('sjis')[-1]) < 0x80 and not (len(
			result[-1]) == 3 and result[-1][-1] == ';' and
			len(result) > 1 and result[-2] == '&#x'):
			t = result.pop()
			result.append(t[:-1])
			result.append(enc(tofull(t[-1])))
		result.append('&#x')
		result.append(s)
	return ''.join(result)

f = open(sys.argv[1])
lines = [line.decode('utf-8').strip().split('\t') for line in f]
f.close()
lines.sort(key=lambda ar: int(ar[0]))
lastpart = 5
for ar in lines:
	assert len(ar) >= 4
	part = int(ar[2])
	if part != lastpart:
		lastpart = part
		print """\
</dl>
</body>
</html>
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""
	print '<dt id="%s">%s</dt>' % tuple(map(enc, ar[:2]))
	for k in ar[3].replace(',', u'，').split(u'，'):
		if k.strip():
			print '<key type="表記">%s</key>' % (tagpat.sub('',
				enc(k.strip())),)
	print '<dd>'
	print '<p>%s %s</p>' % (enc(u'★' * (part - 2)), enc(ar[3]),)
	ltype = len(ar) < 7 and 'u' or 'o'
	print '<%sl>' % (ltype,)
	for i in xrange(1, sys.maxint):
		if 2 + i * 2 >= len(ar):
			break
		print '<li>%s<br>&nbsp;&nbsp;%s</li>' % (enc(ar[2 + i*2]), enc(ar[3 + i*2]))
	print '</%sl>' % (ltype,)
	print '</dd>'
print """\
</dl>
</body>"""

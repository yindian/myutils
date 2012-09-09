#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, sqlite3, re
import pdb

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s db_file' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()
fields = 'aWRpb21faGlyYWdhbmEsIGlkaW9tX2FuZF9leGFtcGxlX2V4LCB0cmFuc2xhdGlvbg=='
c.execute('select %s from Idioms' % (fields.decode('base64'),))

sentpat = re.compile(r'##[0-9]+\^\^')
parenpat = re.compile(r'\(+(.*?)\)+')
stagpat = re.compile(r'<S.*?>(.*?)</S>')
ttagpat = re.compile(r'<T>(.*?)</T>')
ktagpat = re.compile(r'<K>(.*?)</K>')
tagpat = re.compile(r'<.*?>')
sttagpat = re.compile(r'<S[^>]*<T>[^>]*</T>[^>]*>(.*?)</S>')
rbsub = lambda m: parenpat.sub(r'<sub>\g<0></sub>', m.group(1))
xpat = re.compile(r'<X4081>(..)(..)</X4081>', re.I)
def getlastwidth(s, last=False): # False: full, True: half
	if s.endswith('>'):
		return False
	s = tagpat.sub('', xpat.sub('', s.decode('sjis')))
	if not s:
		return last
	return ord(s[-1]) < 0x100
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
	width = getlastwidth(ar[0])
	for s in ar[1:]:
		try:
			p = s.index(';')
			if s[0] == 'x':
				code = int(s[1:p], 16)
			else:
				code = int(s[:p])
			if width:
				s = '<X4081>1F0B</X4081>%04X<X4081>1F0C</X4081>%s' % (code, s[p+1:])
			else:
				s = '<X4081>1F0B</X4081>%s<X4081>1F0C</X4081>%s' % (tofull('%04X' % (code,)).encode('sjis'), s[p+1:])
		except:
			result.append('&#')
		finally:
			result.append(s)
			width = getlastwidth(s, width)
	return ''.join(result)

for pron, mean, trans in c:
	lines = sentpat.split(mean+'^^')[:-1]
	try:
		title = parenpat.sub('', tagpat.sub('', lines[0]))
	except:
		print >> sys.stderr, mean
		raise
	if pron == title:
		print '<dt>【%s】</dt>' % tuple(map(enc, (pron,)))
	else:
		s = '%s【%s】' % tuple(map(enc, (pron, title, )))
		if s.find('<X4081>') < 0:
			print '<dt>%s</dt>' % (s,)
		else:
			print '<dt title="%s">%s</dt>' % (xpat.sub(r'&#x\g<1>;&#x\g<2>;', s), s)
	trans = trans.split('^^')
	assert len(lines) == len(trans)
	for s, t in zip(lines, trans):
		print '<p>'
		s = ttagpat.sub(r'<b>\g<1></b>', stagpat.sub(rbsub, 
			sttagpat.sub(rbsub, s)))
		s = ktagpat.sub(r'\g<1>', s).replace('((', '(').replace('))', ')')
		print '%s<br>' % (enc(s),)
		assert set(tagpat.findall(s)) <= set(['<b>', '</b>', '<sub>',
			'</sub>'])
		print '<indent val="2">%s<indent val="1">' % (enc(t),)
		print '</p>'

c.close()

print """\
</dl>
</body>
</html>"""

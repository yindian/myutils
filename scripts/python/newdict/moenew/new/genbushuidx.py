#!/usr/bin/env python
# -*- coding: sjis -*-
import sys
import pdb, traceback

assert __name__ == '__main__'

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
<title>部首索引</title>
</head>
<body>
<h1>部首索引</h1>"""

d = {}
def f((word, lineno)):
	return '<a href="moedict.htm#m%d">%s</a>' % (lineno, word)
codemap = {
0xE373: 0x7592,
0xE38E: 0x4E28,
0xE398: 0x4EBB,
0xE39B: 0x5DDC,
0xE3A6: 0x5F50,
0xE3A9: 0x5FC4,
0xE3AB: 0x6C35,
0xE3AC: 0x72AD,
0xE3AD: 0x961D,
0xE3B7: 0x8279,
0xE3C2: 0x8FB5,
0xE7B3: 0x8C9F,
0xF6CF: 0x4E36,
0xF6D0: 0x4E3F,
0xF6D1: 0x4E85,
0xF6D2: 0x4EA0,
0xF6D3: 0x5182,
0xF6D4: 0x5196,
0xF6D5: 0x51AB,
0xF6D6: 0x52F9,
0xF6D7: 0x5338,
0xF6D8: 0x5369,
0xF6D9: 0x53B6,
0xF6DA: 0x5902,
0xF6DB: 0x5B80,
0xF6DC: 0x5DDB,
0xF6DD: 0x5E7A,
0xF6DE: 0x5E7F,
0xF6DF: 0x5EF4,
0xF6E0: 0x5F50,
0xF6E1: 0x5F61,
0xF6E2: 0x6534,
0xF6E3: 0x65E0,
0xF6E4: 0x7592,
0xF6E5: 0x7676,
0xF6E6: 0x8FB5,
0xF6E7: 0x96B6,
		}

lineno = 0
for line in open(sys.argv[1]):#sys.stdin:
	lineno += 1
	word, mean = line[:-1].split('\t', 1)
	ar = mean.split('\\n')
	assert ar[0].startswith('詞目')
	try:
		p = ar[0].index('】')
		s = ar[0][p+2:].strip()
	except:
		p = ar[0].index('&#xE285;')
		s = ar[0][p+8:].strip()
	if s:
		try:
			radical, stroke, allstroke = s.split('-')
		except:
			print >> sys.stderr, word.decode('sjis'), s.decode('sjis')
			continue
		if radical == '｜':
			radical = '&#xE38E;'
		stroke = int(stroke)
		if not d.has_key(radical):
			d[radical] = {}
		if not d[radical].has_key(stroke):
			d[radical][stroke] = []
		d[radical][stroke].append((word, lineno))

ar = d.keys()
for i in xrange(len(ar)):
	if ar[i].startswith('&#x'):
		p = ar[i].index(';')
		code = int(ar[i][3:p], 16)
		assert p == len(ar[i])-1
		if codemap.has_key(code):
			code = codemap[code]
		else:
			try:
				assert code < 0xE000
			except:
				print >> sys.stderr, ar[i]
				raise
	else:
		code = ord(ar[i].decode('sjis'))
	ar[i] = (code, ar[i])
ar.sort()

print '<p>'
for code, radical in ar:
	print '<a href="m_%04x">%s</a>' % (code, radical)
print '</p>'
print
for code, radical in ar:
	print '<h2 id="m_%04x">%s</h2>' % (code, radical)
	for stroke in sorted(d[radical]):
		print '<p>%d画</p>' % (stroke,)
		print '<p>%s</p>' % (' '.join(map(f, d[radical][stroke])),)
		print
	print

print """\
</body>
</html>"""

#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, unicodedata
import pdb, traceback

def hw2fw(str):
	return str
	str = str.replace('\\n', '\n').replace('\\\n', '\\\\n')
	str = str.decode('sjis')
	result = []
	ar = str.split('&#')
	for c in ar[0]:
		if 0x41 <= ord(c) <= 0x5A or 0x61 <= ord(c) <= 0x7A:
			result.append(unichr(ord(c) + 0xFEE0))
		else:
			result.append(c)
	for s in ar[1:]:
		p = s.index(';')
		result.append('&#')
		result.append(s[:p+1])
		for c in s[p+1:]:
			if 0x41 <= ord(c) <= 0x5A or 0x61 <= ord(c) <= 0x7A:
				result.append(unichr(ord(c) + 0xFEE0))
			else:
				result.append(c)
	str = u''.join(result).encode('sjis')
	return str.replace('\\n', '\\\n').replace('\n', '\\n')

def fw2hw(str):
	result = []
	for c in str:
		if 0xFF21 <= ord(c) <= 0xFF3A or 0xFF41 <= ord(c) <= 0xFF5A:
			result.append(unichr(ord(c) - 0xFF00 + 0x20))
		else:
			result.append(c)
	return u''.join(result)

def htmlquote(str):
	return str.replace('&', '&amp;').replace('&amp;#', '&#').replace(
			'<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'
					).replace("'", '&apos;')

_hatmap = {
u'\uE29C': u'a',
u'\uE29D': u'a',
u'\uE29E': u'a',
u'\uE29F': u'a',
u'\uE2A0': u'e',
u'\uE2A1': u'e',
u'\uE2A2': u'e',
u'\uE2A3': u'e',
u'\uE2A4': u'i',
u'\uE2A5': u'i',
u'\uE2A6': u'i',
u'\uE2A7': u'i',
u'\uE2A8': u'o',
u'\uE2A9': u'o',
u'\uE2AA': u'o',
u'\uE2AB': u'o',
u'\uE2AC': u'r',
u'\uE2AD': u'r',
u'\uE2AE': u'r',
u'\uE2AF': u'r',
u'\uE2B0': u'u',
u'\uE2B1': u'u',
u'\uE2B2': u'u',
u'\uE2B3': u'u',
u'\uE2B4': u'z',
u'\uE2B5': u'z',
u'\uE2B6': u'z',
u'\uE2B7': u'z',
u'\uEB7C': u'e',
u'\uEC1F': u'a',
u'\uEC20': u'e',
u'\uEC21': u'i',
u'\uEC22': u'o',
u'\uEC23': u'u',
		}
def unhat(str, hatmap=_hatmap):
	str = str.decode('sjis')
	ar = fw2hw(str).split('&#x')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		result.append(unichr(int(s[:p], 16)))
		if hatmap.has_key(result[-1]):
			result[-1] = hatmap[result[-1]]
		result.append(s[p+1:])
	str = u''.join(result).replace(u'\u3000', u' ')
	if str.find(u'(') > 0:
		assert str[str.find(u'('):].startswith(u'(變)')
		str = str[:str.index(u'(')]
	elif str.find(u'（') > 0:
		#assert str[str.find(u'（')+2:].startswith(u'音）')
		str = str[:str.index(u'（')]
	return str.strip().encode('ascii').replace(' ', '')

assert __name__ == '__main__'

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
<title>教育部重編国語辞典修訂本</title>
</head>
<body>"""

lineno = 0
for line in open(sys.argv[1]):#sys.stdin:
	lineno += 1
	word, mean = line[:-1].split('\t', 1)
	pinyin = ''
	ar = htmlquote(hw2fw(mean)).split('\\n')
	for i in xrange(len(ar)):
		if ar[i].startswith('[?'):
			try:
				assert ar[i][2] == 'g'
			except:
				print >> sys.stderr, word.decode('sjis')
				raise
			assert ar[i].endswith(']')
			ar[i] = '<img src="%s" class="inline">' % (ar[i][3:-1],)
	if len(ar) > 3 and ar[3].startswith('通用'):
		pinyin = ar[3][ar[3].index(':')+1:]
		try:
			pinyin = unhat(pinyin)
		except:
			traceback.print_exc()
			pdb.set_trace()
			raise
		print '<dl><dt id="m%d">%s</dt><key type="表記">%s</key><dd>%s</dd></dl>' % (lineno, word, pinyin, '<br>'.join(ar))
	else:
		print '<dl><dt id="m%d">%s</dt><dd>%s</dd></dl>' % (lineno, word, '<br>'.join(ar))

print """\
</body>
</html>"""

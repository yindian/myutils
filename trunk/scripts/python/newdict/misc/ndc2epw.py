#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, struct, re
import pdb

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s target_dat' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

yrpat = re.compile(ur'<span class=yr>(.*?)</span> *')
itupat = re.compile(ur'<itr><itd class="u">(.*?)</itd></itr>')
itdpat = re.compile(ur'<itr><itd class="d">(.*?)</itd></itr>')
def fmt(s):
	s = s.decode('utf-8')
	s = s.replace(u'\u2014', u'\u2015')
	s = yrpat.sub(r'<indent val="1"><b>\g<1></b><br><indent val="2">', s)
	s = itupat.sub(r'<sub>\g<1></sub>', itdpat.sub(r'<sub>\g<1></sub>', s))
	s = s.replace('<itbl>', '').replace('</itbl>', '')
	return s.encode('sjis', 'xmlcharrefreplace')
def isallkana(s):
	for c in s:
		if not 0x3040 < ord(c) < 0x3100:
			return False
	return True
def getenglish(s):
	p = s.find('⇒')
	if p >= 0:
		s = s[:p]
	p = s.find('(&#9654;')
	if p >= 0:
		s = s[:p]
	ar = s.split(';')
	result = []
	for i in xrange(len(ar)):
		t = ar[i].strip()
		p = t.find('(')
		if p > 0 and t.endswith(')'):
			result.append(t[:p].rstrip())
			result.append(t[p+1:-1].strip())
		else:
			result.append(t)
	return filter(None, result)


f = open(sys.argv[1], 'rb')
f.read(8)
wordcount = struct.unpack('<L', f.read(4))[0]
offsets = struct.unpack('<%dL' % (wordcount,), f.read(4*wordcount))
try:
	for i in xrange(wordcount):
		assert f.tell() == offsets[i]
		ar = struct.unpack('<9L', f.read(36))
		length = ar[0]
		assert i == ar[1]
		assert 3 == ar[2]
		assert 36 == ar[3]
		titlelen = ar[4]
		meanoffset = ar[5]-36
		meanlen = ar[6]
		exampleoffset = ar[7]-36
		examplelen = ar[8]
		assert titlelen <= meanoffset
		assert meanoffset + meanlen <= exampleoffset
		assert exampleoffset + examplelen <= length - 36
		s = f.read(length-36)
		title, mean, example = [t.rstrip('\0') for t in 
				s[:titlelen], s[meanoffset:meanoffset
					+meanlen], s[exampleoffset:exampleoffset
						+examplelen]]
		word, pron = title.split('#')
		pron = pron.split(' ')
		print '<dt id="%d">【%s】</dt>' % (i, fmt(word))
		for s in pron:
			s = fmt(s)
			print '<key type="表記">%s</key>' % (s,)
			if isallkana(s.decode('sjis')):
				print '<key type="かな">%s</key>' % (s,)
		for s in getenglish(fmt(mean)):
			print '<key type="表記" title="%s">%s</key>' % (s, s)
		print '<dd>'
		if mean:
			print '<p>%s</p>' % (fmt(mean),)
		if example:
			print '<indent val="2">'
			print '<p>%s</p>' % (fmt(example),)
		print '</dd>'

except:
	print >> sys.stderr, 'Word index', i, 'file offset is', hex(f.tell())
	print >> sys.stderr, ar
	raise
f.close()

print """\
</dl>
</body>
</html>"""

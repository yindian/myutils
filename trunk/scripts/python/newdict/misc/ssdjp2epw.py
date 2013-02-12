#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, sqlite3, re
import os
import pdb, traceback

tonetransform = {
	u'a': u'\u0101\u00E1\u01CE\u00E0',
	u'o': u'\u014D\u00F3\u01D2\u00F2',
	u'e': u'\u0113\u00E9\u011B\u00E8',
	u'i': u'\u012B\u00ED\u01D0\u00EC',
	u'u': u'\u016B\u00FA\u01D4\u00F9',
	u'\u00FC': u'\u01D6\u01D8\u01DA\u01DC',
	u'\u00EA': u'\0\u1EBF\0\u1EC1',
	u'm': u'\0\uE7C7\0\0',
	u'n': u'\0\u0144\u0148\uE7C8',
}
tonedict = {}
for alpha in tonetransform.iterkeys():
	for i in xrange(4):
		if tonetransform[alpha][i]:
			tonedict[tonetransform[alpha][i]] = (alpha, i+1)
hatmap = {
		0x0251: 0x61,
		0x0261: 0x67,
		0x012D: 0x01D0,
		0x0103: 0x01CE,
		0x0115: 0x011B,
		0x016D: 0x01D4,
		0x014F: 0x01D2,
		}
def pinyinuntone(s):
	result = []
	tone = 0
	for c in s.translate(hatmap):
		if c == u'\u00FC':
			c = u'v'
		elif ord(c) >= 0x80:
			c, tone = tonedict[c]
			if c == u'\u00FC':
				c = u'v'
		result.append(c)
	return u''.join(result) + (tone and `tone` or u'')

def half(s):
	result = []
	for c in s:
		cc = ord(c)
		if 0xFF00 <= cc < 0xFF5F:
			result.append(chr(cc - 0xFEE0))
		else:
			result.append(c)
	return u''.join(result)

import codecs
from htmlentitydefs import codepoint2name, name2codepoint
def html_replace(exc):
	assert isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError))
	s = [ u'&%s;' % codepoint2name.get(ord(c), '#x%04X' % (ord(c),))
			for c in exc.object[exc.start:exc.end] ]
	return ''.join(s), exc.end
codecs.register_error('html_replace', html_replace)

charrefxpat = re.compile(r'&#[xX]([0-9A-Fa-f]+);')
def charref2uni(m):
	return unichr(int(m.group(1), 16))
def html_uncharref(s):
	return charrefxpat.sub(charref2uni, s)

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s db_file' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

field='entry_id, word, description, rank, homophone, xml'
c.execute('select %s from entries order by _id ASC' % (field))
f, g = os.popen2('xsltproc snk.xsl -')
print >> f, '''\
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="snk.xsl"?>
<root xmlns:n="urn:xmlns:notknown">'''
for entry_id, word, description, rank, homophone, xml in c:
	try:
		xml = str(xml).decode('zlib').decode('utf-8')
		#print '\t'.join([entry_id, word, xml]).encode('utf-8')
#		f = open('xml/%s.xml' % (entry_id,), 'w')
#		print >> f, '''\
#<?xml version="1.0" encoding="UTF-8"?>
#<?xml-stylesheet type="text/xsl" href="snk.xsl"?>
#<root xmlns:n="urn:xmlns:notknown">'''
		print >> f, xml.encode('utf-8')
		#print >> f, '</root>'
		#f.close()
	except:
		print >> sys.stderr, 'Error processing id', word
		traceback.print_exc()
		raise
print >> f, '</root>'
f.close()

f = open('out.htm', 'w')
print >> f, """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>"""

g.readline()
buf = g.read()
g.close()
buf = html_uncharref(buf.decode('utf-8'))
f.write(buf.encode('sjis', 'html_replace'))

print >> f, "</html>"
f.close()

sys.exit()

f = open('GaijiMap.xml', 'w')
print >> f, """\
<?xml version="1.0" encoding="Shift_JIS"?>
<gaijiSet>"""

idx2ebc = lambda x: '%02X%02X' % (x / 94 + 0xA1, x % 94 + 0x21)
half = False
idx = 0
for code in sorted(gaijiset):
        if code < 0x2000:
                half = True
        print >> f, '<gaijiMap name="%d" unicode="#x%04X" ebcode="%s"/>' % (
                        code, code, idx2ebc(idx))
        idx += 1
print >> f, '</gaijiSet>'
f.close()

f = open('Gaiji.xml', 'w')
print >> f, """\
<?xml version="1.0" encoding="Shift_JIS"?>
<gaijiData xml:space="preserve">
<fontSet size="%dX16" start="A121">""" % (half and 8 or 16,)
idx = 0
for code in sorted(gaijiset):
        if code >= 0x2000 and half:
                print >> f, '</fontSet><fontSet size="16X16" start="%s">' % (
                                idx2ebc(idx),
                                )
                half = False
        p = os.popen('fontdumpw "%s" 0x%04X -e=%s%s' % (
                half and "Tahoma" or "MingLiU", code, idx2ebc(idx),
                half and ' -x=8' or ''))
        f.write(p.read())
        p.close()
        idx += 1
print >> f, """\
</fontSet>
</gaijiData>"""
f.close()


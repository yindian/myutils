#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, sqlite3, re
import os
import pdb, traceback

import codecs
from htmlentitydefs import codepoint2name, name2codepoint
supported_entities = set('''\
lt
gt
amp
quot
apos
iexcl
cent
pound
curren
yen
brvbar
sect
uml
copy
ordf
laquo
not
shy
reg
macr
deg
plusmn
sup2
sup3
acute
micro
para
middot
cedil
sup1
ordm
raquo
frac14
frac12
frac34
iquest
Agrave
Aacute
Acirc
Atilde
Auml
Aring
AElig
Ccedil
Egrave
Eacute
Ecirc
Euml
Igrave
Iacute
Icirc
Iuml
ETH
Ntilde
Ograve
Oacute
Ocirc
Otilde
Ouml
times
Oslash
Ugrave
Uacute
Ucirc
Uuml
Yacute
THORN
szlig
agrave
aacute
acirc
atilde
auml
aring
aelig
ccedil
egrave
eacute
ecirc
euml
igrave
iacute
icirc
iuml
eth
ntilde
ograve
oacute
ocirc
otilde
ouml
divide
oslash
ugrave
uacute
ucirc
uuml
yacute
thorn
yuml
Amacr
amacr
Abreve
abreve
Aogon
aogon
Cacute
cacute
Ccirc
ccirc
Cabove
cabove
Ccaron
ccaron
Dcaron
dcaron
Dstrok
dstrok
Emacr
emacr
Ebreve
ebreve
Eabove
eabove
Eogon
eogon
Ecaron
ecaron
Gcirc
gcirc
Gbreve
gbreve
Gabove
gabove
Gcedil
gcedil
Hcirc
hcirc
Hstrok
hstrok
Itilde
itilde
Imacr
imacr
Ibreve
ibreve
Iogon
iogon
Iabove
inodot
IJlig
ijlig
Jcirc
jcirc
Kcedil
kcedil
kgreen
Lacute
lacute
Lcedil
lcedil
Lcaron
lcaron
Lmidot
lmidot
Lstrok
lstrok
Nacute
nacute
Ncedil
ncedil
Ncaron
ncaron
napos
ENG
eng
Omacr
omacr
Obreve
obreve
Odblac
odblac
OElig
oelig
Racute
racute
Rcedil
rcedil
Rcaron
rcaron
Sacute
sacute
Scirc
scirc
Scedil
scedil
Scaron
scaron
Tcedil
tcedil
Tcaron
tcaron
Tstrok
tstrok
Utilde
utilde
Umacr
umacr
Ubreve
ubreve
Uring
uring
Udblac
udblac
Uogon
uogon
Wcirc
wcirc
Ycirc
ycirc
Yuml
Zacute
zacute
Zabove
zabove
Zcaron
zcaron
fnof
circ
tilde'''.splitlines())
mycodepoint2name = dict(zip(supported_entities, map(name2codepoint.get, supported_entities)))
def html_replace(exc):
	assert isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError))
	s = [ u'&%s;' % mycodepoint2name.get(ord(c), '#x%04X' % (ord(c),))
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
#f = open('obs.xml', 'w')
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

#sys.exit()

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
buf = buf.replace('<dd> ', '<dd>').replace('<dd> ', '<dd>')
buf = buf.encode('sjis', 'html_replace')
f.write(buf)

print >> f, "</html>"
f.close()

sys.exit()

f = open('out.htm', 'r')
buf = f.read()
f.close()

gaijiset = set([int(s, 16) for s in charrefxpat.findall(buf)])

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

import numpy
import freetype
face = freetype.Face('tategaki.ttf')
face.set_char_size(16*64)

def bits(x):
	data = []
	for i in range(8):
		data.insert(0, int((x & 1) == 1))
		x = x >> 1
	return data

f = open('Gaiji.xml', 'w')
print >> f, """\
<?xml version="1.0" encoding="UTF-8"?>
<gaijiData xml:space="preserve">
<fontSet size="%dX16" start="A121">""" % (half and 8 or 16,)
idx = 0
for code in sorted(gaijiset):
        if code >= 0x2000 and half:
                print >> f, '</fontSet>\n<fontSet size="16X16" start="%s">' % (
                                idx2ebc(idx),
                                )
                half = False
	face.load_char(unichr(code), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
	bitmap = face.glyph.bitmap
	left   = face.glyph.bitmap_left
	top    = face.glyph.bitmap_top
	data = []
	for i in range(bitmap.rows):
		row = []
		for j in range(bitmap.pitch):
			row.extend(bits(bitmap.buffer[i*bitmap.pitch+j]))
		data.extend(row[:bitmap.width])
	img = numpy.array(data).reshape(bitmap.rows, bitmap.width)
	try:
		if len(img) < 16:
			img = numpy.vstack([[0] * len(img[0])] * (8 - top) + [img] + [[0] * len(img[0])] * (top + 8 - len(img)))
		assert len(img) == 16
		if not half:
			if len(img[0]) < 16:
				if len(img[0]) + left > 16:
					left = 16 - len(img[0]) - (16 - len(img[0])) / 2
				img = numpy.column_stack([[0] * 16] * (left + (16 - len(img[0]) - left) / 2) + [img] + [[0] * 16] * (16 - len(img[0]) - left - (16 - len(img[0]) - left) / 2))
			assert len(img[0]) == 16
		else:
			if len(img[0]) < 8:
				img = numpy.column_stack([[0] * 16] * (left + (8 - len(img[0]) - left) / 2) + [img] + [[0] * 16] * (8 - len(img[0]) - left - (8 - len(img[0]) - left) / 2))
			assert len(img[0]) == 8
	except:
		print >> sys.stderr, hex(code), unichr(code), bitmap.rows, bitmap.width, top, left
		#traceback.print_exc()
		#raise
	if not half:
		img = numpy.rot90(img, -1)
	print >> f, '<fontData ebcode="%s" unicode="%04X"> <!-- %s -->' % (idx2ebc(idx), code, unichr(code).encode('utf-8'))
	for row in img:
		for col in row:
			f.write(' #'[col])
		print >> f
	print >> f, '</fontData>'
        idx += 1
print >> f, """\
</fontSet>
</gaijiData>"""
f.close()


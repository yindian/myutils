#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os
print """\
<?xml version="1.0" encoding="Shift_JIS"?>
<gaijiSet>"""
print >> sys.stderr, """\
<?xml version="1.0" encoding="Shift_JIS"?>
<gaijiData xml:space="preserve">
<fontSet size="16X16" start="A121">"""

lineno = 0
for line in open(sys.argv[1]):#sys.stdin:
	line = line.split()
	code = int(line[0], 16)
	if len(line) < 3 or not line[2].strip():
		print '<gaijiMap name="%d" unicode="#x%04X" ebcode="%02X%02X"/>' % (code, code, (0x21 + lineno / 94), (0x21 + lineno % 94))
	else:
		print '<gaijiMap name="%d" unicode="#x%04X" ebcode="%02X%02X" alt="%s"/>' % (code, code, (0x21 + lineno / 94), (0x21 + lineno % 94), line[2].strip())
	if 0xE000 <= code < 0xF900:
		fontname = 'EUDC'
	else:
		fontname = 'MingLiU'
	p = os.popen('FontDumpW "%s" %04X -e=%02X%02X' % (fontname, code, 
		(0x21 + lineno / 94), (0x21 + lineno % 94)))
	sys.stderr.write(p.read())
	p.close()
	lineno += 1

print """\
</gaijiSet>"""
print >> sys.stderr, """\
</fontSet>
</gaijiData>"""

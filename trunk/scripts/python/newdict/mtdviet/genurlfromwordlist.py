#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, unicodedata, urllib2

assert __name__ == '__main__'

if len(sys.argv) != 3:
	print "Usage: %s chv.txt vch.txt" % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

urltemplate = 'http://www.vietgle.vn/tratu/tu-dien-truc-tuyen.aspx?k=%s&t=%s'

f = open(sys.argv[1], 'r')
for line in f:
	line = line.strip()
	if not line or line == '?':
		continue
	print urltemplate % (urllib2.quote(line), 'T-V')
	if line == '进取':
		print urltemplate % (urllib2.quote('进去'), 'T-V')
	elif line == '力不从心':
		print urltemplate % (urllib2.quote('力持'), 'T-V')
f.close()

norm = lambda s: unicodedata.normalize('NFC', s.decode('utf-8')).encode('utf-8')
f = open(sys.argv[2], 'r')
for line in f:
	line = line.strip()
	if not line or line == '?':
		continue
	line = norm(line)
	print urltemplate % (urllib2.quote(line), 'V-T')
	if line == norm('thế trận sinh tử'):
		print urltemplate % (urllib2.quote(norm('thế trội')), 'V-T')
	elif line == norm('thế vai'):
		print urltemplate % (urllib2.quote(norm('thế vận')), 'V-T')
f.close()

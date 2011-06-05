#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, sqlite3, re
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

escmap = {
		0x3c: u'&lt;',
		0x3e: u'&gt;',
		0x26: u'&amp;',
		0x22: u'&quot;',
		#0x27: u'&apos;',
		}
def html_escape(s):
	return unicode(s).translate(escmap)
enc = lambda s: html_escape(s).encode('cp932', 'html_replace')

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s db_file' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

f = open('out.htm', 'w')
print >> f, """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

charrefpat = re.compile(r'&#x(.*?);')
delimpat = re.compile(ur'[，。；]')
punctpat = re.compile(ur'[・／、（）…\u00B7“あまり”〔〕]')

field='wid, wtypeid, wname, wspellall, wjpname, wjpspellall, wcontent, wexample, wsound, hsklvl, zjlvl, srchnum'
c.execute(('select %s from word order by srchnum DESC' % (field.replace('w', 'word').replace('lvl', 'level'))).replace('srch', 'search'))
wordmap = {}
freqord = []
for wid, wtypeid, wname, wspellall, wjpname, wjpspellall, wcontent, wexample, wsound, hsklvl, zjlvl, srchnum in c:
	if wname in (u'プジョー', u'レセプト', u'中国結び', u'知りあう', u'落胆感', u'車の車体', u'障害物', u'変装', u'催促する', u'摘出'):
		wname, wspellall, wjpname, wjpspellall = wjpname, wjpspellall, wname, wspellall
	if wname in (u'ぶらいずめいど',):
		wname, wspellall, wjpname, wjpspellall = wjpname, wjpspellall, wspellall, wname
	elif len(wspellall) < 3 and wspellall in (u'村', u'瓣', u'上\u5934', u'\u5706', u'上\u5C42', u'口', u'\u7EFF', u'硬'):
		wname, wspellall = wspellall, wname
	elif wname == u'毫不起眼':
		wspellall = u'h\u00E1o b\u00F9 q\u01D0 y\u01CEn'
	elif wname == u'金' and len(wspellall) == 1:
		wspellall = u'j\u012Bn'
	elif wname == u'撤\u9500':
		wspellall = u'ch\u00E8 xi\u0101o'
	elif wname == u'\u03A3':
		wspellall = u'sigma'
	elif wname.startswith(u'不良住房') and wname.endswith(u'症'):
		wspellall = u'b\u00F9 li\u00E1ng zh\u00F9 f\u00E1ng z\u014Dng h\u00E9 zh\u00E8ng' + wspellall[wspellall.index(u'，'):]
	elif len(wspellall) == 1:
		if wname == u'角':
			wspellall = u'ji\u01CEo'
		elif wname == u'密':
			wspellall = u'm\u00EC'
		elif wname == u'算':
			wspellall = u'su\u00E0n'
		elif wname == u'狠':
			wspellall = u'h\u011Bn'
		elif wname == u'少':
			wspellall = u'sh\u01CEo'
		elif wname == u'点':
			wspellall = u'di\u01CEn'
	elif wname == u'一向':
		wspellall = u'y\u00ED xi\u00E0ng'
	elif wname == u'比べる':
		wname, wspellall, wjpname, wjpspellall = u'比', u'b\u01D0', wname, wspellall
	wordmap[wid] = (wtypeid, wname, wspellall, wjpname, wjpspellall, wcontent, wexample, wsound, hsklvl, zjlvl, srchnum)
	freqord.append((srchnum, wid))
	try:
		ewn = enc(wname)
		if len(ewn) + len(wspellall) <= 64:
			print >> f, '<dt id="%d">【%s】%s</dt>' % (wid, ewn, enc(wspellall))
		else:
			print >> f, '<dt id="%d" title="%s">【%s】%s</dt>' % (wid, enc((u'【%s】%s' % (wname, wspellall))[:32]), ewn, enc(wspellall))
		if delimpat.findall(wname):
			for word in delimpat.split(wname):
				print >> f, '<key type="表記">%s</key>' % (charrefpat.sub(r'\g<1>', enc(word)),)
		elif ewn.find('&#x') >= 0:
			print >> f, '<key type="表記">%s</key>' % (charrefpat.sub(r'\g<1>', ewn),)
		for spell in delimpat.split(half(punctpat.sub('', wspellall))):
			pin1yin1 = ''.join(map(pinyinuntone, spell.lower().split())).encode('ascii')
			print >> f, '<key type="表記">%s</key>' % (pin1yin1,)
			pinyin = ''.join(filter(lambda c: not c.isdigit(), pin1yin1))
			if pinyin != pin1yin1:
				print >> f, '<key type="表記">%s</key>' % (pinyin,)
		print >> f, '<key type="かな" title="%s【%s】%s">%s</key>' % (enc(wjpname), enc(wname), enc(wspellall), enc(wjpspellall))
		print >> f, '<key type="条件" title="【%s】%s %s">%s</key>' % (enc(wjpname), enc(wjpspellall), enc(wname), enc(wjpname))
		print >> f, '<dd>'
		print >> f, '&nbsp;<a href="toc.htm#%d">↑</a><br>' % (wid,)
		print >> f, '【%s】%s<br>' % (enc(wjpname), enc(wjpspellall))
		if wcontent.strip():
			print >> f, '<indent val="1">解釈&nbsp;&nbsp;<indent val="3">%s<br>' % (enc(wcontent).replace('\\n', '<br>'),)
		if wexample.strip():
			print >> f, '<indent val="1">例文&nbsp;&nbsp;<indent val="3">%s<br>' % (enc(wexample).replace('\\n', '<br>'),)
		print >> f, '</dd>'
		print >> f, '<div><br></div>'
	except:
		print >> sys.stderr, 'Error processing id', wid
		traceback.print_exc()
		raise
c.close()

print >> f, """\
</dl>
</body>
</html>"""
f.close()

g = open('toc.htm', 'w')
print >> g, '<html>\n<body>'
print >> g, '<p>'
c.execute(('select %s from WBT order by WBTsort' % ('WBTid, WBTname',)).replace('W', 'word').replace('B', 'big').replace('T', 'type'))
wbtlist = []
for wbtid, wbtname in c:
	print >> g, '<div id="_b%d"><a href="b%d">%s</a><br></div>' % (wbtid, wbtid, enc(wbtname))
	wbtlist.append((wbtid, wbtname))
print >> g, '</p>'
for wbtid, wbtname in wbtlist:
	print >> g, '<h1 id="b%d">%s</h1>' % (
			wbtid, enc(wbtname))
	print >> g, '<p>'
	c.execute(('select %s from WMT where WBTid = %d order by WMTsort' % ('WMTid, WMTname', wbtid)).replace('W', 'word').replace('B', 'big').replace('M', 'middle').replace('T', 'type'))
	wmtlist = []
	for wmtid, wmtname in c:
		print >> g, '<div id="_m%d"><a href="m%d">%s</a> <a href="_b%s">↑</a><br></div>' % (
				wmtid, wmtid, enc(wmtname), wbtid)
		wmtlist.append((wmtid, wmtname))
	if wmtlist:
		print >> g, '</p>'
		for wmtid, wmtname in wmtlist:
			print >> g, '<h2 id="m%d">%s</h2>' % (wmtid, enc(wmtname))
			print >> g, '<p>'
			c.execute(('select %s from WT where WMTid = %d' % ('WTid, WTname', wmtid)).replace('W', 'word').replace('B', 'big').replace('M', 'middle').replace('T', 'type'))
			wtlist = []
			for wtid, wtname in c:
				print >> g, '<div id="_t%d"><a href="t%d">%s</a> <a href="_m%s">↑</a><br></div>' % (
						wtid, wtid, enc(wtname), wmtid)
				wtlist.append((wtid, wtname))
			print >> g, '</p>'
			for wtid, wtname in wtlist:
				print >> g, '<h3 id="t%d">%s</h2>' % (wtid, enc(wtname))
				print >> g, '<p>'
				c.execute(('select %s from W where WTid = %d' % ('Wid, Wname', wtid)).replace('W', 'word').replace('B', 'big').replace('M', 'middle').replace('T', 'type'))
				for wid, wname in c:
					print >> g, '<div id="%d"><a href="out.htm#%d">%s</a> <a href="_t%d">↑</a><br></div>'%(wid, wid, enc(wname), wtid)
				print >> g, '</p>'
	else:
		c.execute(('select %s from WT where WBTid = %d' % ('WTid, WTname', wbtid)).replace('W', 'word').replace('B', 'big').replace('M', 'middle').replace('T', 'type'))
		wtlist = []
		for wtid, wtname in c:
			print >> g, '<div id="_t%d"><a href="t%d">%s</a> <a href="_b%s">↑</a><br></div>' % (
					wtid, wtid, enc(wtname), wbtid)
			wtlist.append((wtid, wtname))
		print >> g, '</p>'
		for wtid, wtname in wtlist:
			print >> g, '<h2 id="t%d">%s</h2>' % (wtid, enc(wtname))
			print >> g, '<p>'
			c.execute(('select %s from W where WTid = %d' % ('Wid, Wname', wtid)).replace('W', 'word').replace('B', 'big').replace('M', 'middle').replace('T', 'type'))
			for wid, wname in c:
				print >> g, '<div id="%d"><a href="out.htm#%d">%s</a> <a href="_t%d">↑</a><br></div>'%(wid, wid, enc(wname), wtid)
			print >> g, '</p>'
print >> g, '</body>\n</html>'
g.close()

sys.exit(0)

gaijiset = set()
for fn in ('out.htm', 'toc.htm'):
        f = open(fn, 'r')
        for line in f:
                ar = line.split('&')
                for i in xrange(1, len(ar)):
                        p = ar[i].index(';')
                        if ar[i].startswith('#x'):
                                code = int(ar[i][2:p], 16)
			elif ar[i].startswith('#'):
                                code = int(ar[i][1:p])
			else:
				code = name2codepoint[ar[i][:p]]
			if code > 0x7F:
				gaijiset.add(code)
        f.close()

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


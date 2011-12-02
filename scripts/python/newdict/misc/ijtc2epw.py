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
<body>"""

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

sentpat = re.compile(r'@@[0-9]+\^\^')
parenpat = re.compile(r'\((.*?)\)')
tagpat = re.compile(r'<.*?>')
xpat = re.compile(r'<X4081>(..)(..)</X4081>', re.I)
rbpat = re.compile(r'<K>(.*?)</K><H>(.*?)</H>')
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

tonemap = {
		0x24ea: u'\ue000',
		0x2460: u'\ue001',
		0x2461: u'\ue002',
		0x2462: u'\ue003',
		0x2463: u'\ue004',
		0x2464: u'\ue005',
		0x2465: u'\ue006',
		0x2466: u'\ue007',
		0x2467: u'\ue008',
		0x2468: u'\ue009',
		0x2469: u'\ue00a',
		0x246a: u'\ue00b',
		0x246b: u'\ue00c',
		0x246c: u'\ue00d',
		0x246d: u'\ue00e',
		0x246e: u'\ue00f',
		0x246f: u'\ue010',
		0x2470: u'\ue011',
		0x2471: u'\ue012',
		0x2472: u'\ue013',
		0x2473: u'\ue014',
		}
tonepat = re.compile(ur'([%s])' % (u''.join(map(unichr, tonemap.keys()))))
circmap = {
		u'例': u'\ue015',
		u'同': u'\ue016',
		u'反': u'\ue017',
		}

fields = 'TlVNQkVSLCBLQU5BLCBLQU5aSSwgQUNDRU5ULCBHUkFNTUFSLCBTWU5PTllNLCBBTlRPTllNLCBDT1VOVFVTQUdFLCBQT1MsIFdPUkRTT1VORCwgVFJBTlNMQVRJT04sIEVU'
c.execute('select %s from jcwords' % (fields.decode('base64'),))
out = sys.stdout.write
for num,kana,kanji,tone,conjug,syn,ant,kazoe,hinsi,snd,trans,et in c:
	print '<dl>'
	pron = kana + tone.translate(tonemap)
	title = kanji #parenpat.sub('', kanji)
	if not title:
		print '<dt id="%s">%s</dt>' % tuple(map(enc, (num, pron,)))
	else:
		s = '%s【%s】' % tuple(map(enc, (pron, title)))
		if s.find('<X4081>') < 0:
			print '<dt id="%s">%s</dt>' % (enc(num), s,)
		else:
			print '<dt id="%s" title="%s">%s</dt>' % (enc(num),
					enc2title(s), s)
		title = parenpat.sub('', kanji)
		if title != kanji:
			print '<key type="表記">%s</key>' % (tagpat.sub('',
				enc(title)),)
	out('<dd>')
	if hinsi:
		if not kazoe:
			out('［%s］<br>' % tuple(map(enc, (hinsi,))))
		else:
			out('［%s］［%s］<br>' % tuple(map(enc, (hinsi, kazoe))))
	elif kazoe:
		out('［%s］<br>' % tuple(map(enc, (kazoe,))))
	maxcnt = trans.count('&&')
	result = []
	for syn in syn.split('||'):
		ar = tonepat.split(syn)
		if len(ar) == 1:
			syn = [syn] if syn else []
		else:
			syn = []
			for i in xrange(1, len(ar), 2):
				syn.append((ar[i], ar[i+1]))
		result.append(syn)
	while len(result) < maxcnt:
		result.append([])
	syn = result
	result = []
	for ant in ant.split('||'):
		ar = tonepat.split(ant)
		if len(ar) == 1:
			ant = [ant] if ant else []
		else:
			ant = []
			for i in xrange(1, len(ar), 2):
				ant.append((ar[i], ar[i+1]))
		result.append(ant)
	while len(result) < maxcnt:
		result.append([])
	ant = result
	first = True
	for syn, ant, trans in zip(syn, ant, trans.split('&&')):
		if trans and 0x2160 <= ord(trans[0]) < 0x2180:
			trans = trans[1:]
		if trans.startswith('('):
			p = trans.index(')') + 1
			while trans[p] == '(':
				p = trans.index(')', p) + 1
			hinsi = trans[:p]
			out('%s<br>' % (enc(hinsi),))
			trans = trans[p:]
		trans = trans.split('||')
		for line in trans:
			if not line: continue
			indented = False
			if ord(line[0]) in tonemap:
				#out('<indent val="1">%s<indent val="2">' % (
				out('%s' % (
						enc(line[0].translate(tonemap)),))
				idx = line[0]
				line = line[1:]
				indented = True
			ar = line.split(';;')
			assert len(ar) <= 2
			if not ar: continue
			if ar[0].find('%%') < 0:
				out(enc(ar[0]))
				out('<br>')
			else:
				aar = ar[0].split('%%')
				out(enc(aar[0]))
				out('<br><indent val="2">')
				for s in aar[1:]:
					br = s.split('##')
					cr = br[0].split('$$')
					assert len(cr) == 2
					out('%s／%s<br>' % tuple(map(enc, cr)))
				out('<indent val="1">')
			#if indented:
			#	out('<indent val="1">')
			if len(ar) == 2:
				out(enc(circmap[u'例']))
				for ex in ar[1].split('^^'):
					br = ex.split('##')
					cr = br[0].split('$$')
					assert len(cr) == 2
					out('%s／%s<br><indent val="2">' % tuple(map(enc, cr)))
				out('<indent val="1">')
			if syn:
				if not indented:
					try:
						assert type(syn[0]) != tuple
					except:
						if kana in [u'けしかける']or\
								(kanji in [
									u'転入',
									u'鳥打ち',
									u'伏せ字',
									u'留保'
									]):
							syn[0] = ''.join(syn[0])
						else:
							raise
					out('%s%s<br>' % tuple(map(enc, [
						circmap[u'同'], syn[0]])))
					del syn[0]
				elif syn[0][0] == idx:
					out('%s%s<br>' % tuple(map(enc, [
						circmap[u'同'], syn[0][1]])))
					del syn[0]
			if ant:
				if kanji == u'shakehand' and not indented:
					indented = True
					idx = u'\u2460'
				if not indented:
					try:
						assert type(ant[0]) != tuple
					except:
						if kanji in [u'開館', u'転入',
								u'理科',
								u'立体']:
							ant[0] = ''.join(ant[0])
						else:
							raise
					out('%s%s<br>' % tuple(map(enc, [
						circmap[u'反'], ant[0]])))
					del ant[0]
				elif ant[0][0] == idx:
					out('%s%s<br>' % tuple(map(enc, [
						circmap[u'反'], ant[0][1]])))
					del ant[0]
			#out('<br>')
		first = False

	print '</dd>\n</dl>\n'
print """\
</body>
<body>"""

fields = 'TlVNQkVSLEtFWVdPUkQsVFJBTlNMQVRJT04sRVQ='
c.execute('select %s from cjwords' % (fields.decode('base64'),))
for num,key,trans,et in c:
	print '<dl>'
	s = '【%s】' % (enc(key),)
	if s.find('<X4081>') < 0:
		print '<dt id="c%s">%s</dt>' % (enc(num), s,)
	else:
		print '<dt id="c%s" title="%s">%s</dt>' % (enc(num),
				enc2title(s), s)
	out('<dd>')
	trans = rbpat.sub(r'<ruby><rb>\g<1></rb><rt>\g<2></rt></ruby>', trans)
	for trans in trans.split('&&'):
		trans = trans.split('||')
		for line, lineno in zip(trans, xrange(1, sys.maxint)):
			if not line: continue
			ar = line.split(';;')
			assert len(ar) <= 2
			if not ar: continue
			if lineno > 1 or len(trans) > 1:
				out(enc(unichr(0xe000 + lineno)))
			if ar[0].find('##') < 0:
				out(enc(ar[0]))
				out('<br>')
			else:
				aar = ar[0].split('##')
				out(enc(aar[0]))
				out('<br>')
	print '</dd>\n</dl>\n'

c.close()

print """\
</body>
</html>"""

exit()

gaijimap = {}
for k, v in tonemap.iteritems():
	gaijimap[ord(v)] = k
for k, v in circmap.iteritems():
	gaijimap[ord(v)] = ord(k)
gaijiset = set(gaijimap.keys())

f = open('GaijiMap.xml', 'w')
print >> f, """\
<?xml version="1.0" encoding="Shift_JIS"?>
<gaijiSet>"""

idx2ebc = lambda x: '%02X%02X' % (x / 94 + 0xA1, x % 94 + 0x21)
half = False
idx = 0
for code in sorted(gaijiset):
        if gaijimap.get(code, code) < 0x2000:
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
        code = gaijimap.get(code, code)
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

################
#   #    #   # #
#   ######   # #
#   # #    # # #
#  ## #### # # #
# ##  #  # # # #
## #  #  # # # #
#  # # ### # # #
#  # #   # # # #
#  #    #  # # #
#  #    #  # # #
#  #   #     # #
#  #  #      # #
#  # #     ### #
#  #        #  #
################

################
# #          # #
# ##############
# #          # #
# #       #  # #
# # ######## # #
# #          # #
# #  #    #  # #
# #  ######  # #
# #  #    #  # #
# #  ######  # #
# #  #    #  # #
# #          # #
# #        ### #
# #         #  #
################

################
#  #         # #
#  #############
#  #           #
#  #        #  #
#  ########### #
#  # #      #  #
#  #  #    #   #
#  #  #    #   #
#  #   #  #    #
#  #    ##     #
# #    # #     #
# #   #   ##   #
# #  #      ####
##  ##        ##
################

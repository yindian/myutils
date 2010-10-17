#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, struct
import pdb

BEGINMAGIC = '\x00\x00\x00\x18\x04\x00'
ENDMAGIC   = '\x00\x00\x00\x00\x04\x00'

# Control codes (big endian)
# 2100 len		heading, followed by len chars and null
# 0200 len		intonation, followed by len chars
# 0B00 len		kanji, followed by len chars
# 1300 len		PoS, followed by len chars
# 0500 len		meaning item, followed by len chars
# 0A00 len		example, followed by len chars
# 0600 len		synonym, followed by len chars
# 0300 len		unknown, maybe index?; alt PoS, Cf 1300
# 1500 len		meaning item, followed by len chars. Cf 0500
# 0000 ???		ignore ???
# A100 len		sub heading, followed by len chars and null
# 0400 len		idiom, followed by len chars
# 0900 len		derivation, followed by len chars
# 0700 len		reference, followed by len chars
# 1B00 len		alt kanji, followed by len chars. Cf 0B00
# 1200 len		alt intonation, followed by len chars. Cf 0200
CTL_IGN_SET  = (0x0300, 0x0000)
CTL_HEAD_SET = (0x2100, 0xA100)
CTL_CODE_SET = (
		0x2100,
		0x0200,
		0x0B00,
		0x1300,
		0x0500,
		0x0A00,
		0x0600,
		0x0300,
		0x1500,
		0xA100,
		0x0400,
		0x0900,
		0x0700,
		0x1B00,
		0x1200,
		)

def prebody():
	pass

def postbody():
	pass

stripmark = lambda s: s.replace(u'\u25bd', u'').replace(u'\u25bc', u'').strip()
htmlquote = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace(
		'>', '&gt;').replace('\n', '').replace('\r', '')
def unbracket(str):
	p = str.find('(')
	if p < 0: return str
	q = str.index(')', p)
	pre = str[:p].rstrip()
	mid = str[p+1:q].strip()
	post = str[q+1:].lstrip()
	return '%s%s|%s%s%s' % (pre, unbracket(post), pre, mid, unbracket(post))

def flushitem(item):
	word = []
	mean = [[]]
	pendingpos = None
	for ctl, str in item:
		if ctl in CTL_HEAD_SET:
			word.append(str.replace(u'\u00b7', u''))
		elif ctl in (0x0B00, 0x1B00): # kanji
			word.extend(map(unbracket, map(stripmark, str.split(u'\u00b7'))))
		if   ctl == 0x2100 or ctl == 0xA100: #heading
			assert len(mean) == 1
			mean[0].append('<big>')
			mean[0].append(htmlquote(str))
			mean[0].append('</big>')
		elif ctl == 0x0200: #intonation
			assert len(mean) == 1
			mean[0].append('<c>')
			mean[0].append(htmlquote(str))
			mean[0].append('</c>')
		elif ctl == 0x0B00: #kanji
			if len(mean) == 1:
				mean[0].append(u'<c>\u3010')
				mean[0].append(htmlquote(str))
				mean[0].append(u'\u3011</c>')
			else: # same as 1B00
				if not pendingpos: pendingpos = u''
				pendingpos += u'<c>\u3010%s\u3011</c>' % (htmlquote(str),)
		elif ctl == 0x0500 or ctl == 0x1500: #meaning item
			if pendingpos:
				mean.append([pendingpos + htmlquote(str)])
				pendingpos = None
			else:
				mean.append([htmlquote(str)])
		elif ctl == 0x0300 or ctl == 0x1300: #PoS
			if not pendingpos: pendingpos = u''
			pendingpos += u'\u3008%s\u3009' % (htmlquote(str),)
		elif ctl == 0x1200: #alt intonation
			if not pendingpos: pendingpos = u''
			pendingpos += u'<c>%s</c>' % (htmlquote(str),)
		elif ctl == 0x1B00: #alt kanji
			if not pendingpos: pendingpos = u''
			pendingpos += u'<c>\u3010%s\u3011</c>' % (htmlquote(str),)
		elif ctl == 0x0A00: #example
			if len(mean) == 1:
				mean.append(pendingpos and [pendingpos] or [])
			mean[-1].append(u'<ex>%s</ex>' % (htmlquote(str),))
		elif ctl == 0x0400: #idiom
			if len(mean) == 1:
				mean.append(pendingpos and [pendingpos] or [])
			mean[-1].append(u'<b>慣用</b>: ' + htmlquote(str))
		elif ctl == 0x0600: #synonym
			if len(mean) == 1:
				mean.append(pendingpos and [pendingpos] or [])
			mean[-1].append(u'<b>同義</b>: ' + htmlquote(str))
		elif ctl == 0x0700: #reference
			try:
				assert len(mean) > 1
			except:
				print >> sys.stderr, u'|'.join(word).encode(
						'gbk', 'replace')
				raise
			assert len(mean) > 1
			mean[-1].append(u'<b>參照</b>: ' + htmlquote(str))
		elif ctl == 0x0900: #derivation
			assert len(mean) > 1
			mean[-1].append(u'<b>派生</b>: ' + htmlquote(str))
	result = [u'|'.join(word), u'\t']
	result.append(u''.join(mean[0]))
	result.append(u'\\n')
	if len(mean) > 1:
		if len(mean) == 2:
			result.append(u'\\n'.join(mean[1]))
			result.append(u'\\n')
		else:
			for i in xrange(1, len(mean)):
				result.append('<b>%d.</b>' % (i,))
				result.append(u'\\n'.join(mean[i]))
				result.append(u'\\n')
		if result[-1] == u'\\n': del result[-1]
		print u''.join(result).strip().encode('utf-8')

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s DH_file_name' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'rb')
buf = f.read()
f.close()

first = True
p = buf.find(BEGINMAGIC)
while p >= 0:
	q = buf.find(ENDMAGIC, p)
	#print p, q
	if q < 0:
		q = len(buf)
	else:
		q -= 8
	p += 20
	#if not first: pdb.set_trace()
	last = []
	prebody()
	while p < q:
		try:
			ctl, l = struct.unpack('!HH', buf[p:p+4])
		except:
			break
		if ctl in CTL_HEAD_SET and last:
			flushitem(last)
			last = []
		p += 4
		if p > q:
			assert ctl == 0
			break
		if ctl in CTL_IGN_SET and not first:
			p += 2*l
			continue
		str = buf[p:p+2*l]
		try:
			str = str.decode('utf-16le')
			assert ctl in CTL_CODE_SET
		except:
			print >> sys.stderr, p, hex(p), hex(ctl), hex(l)
			raise
		#print hex(ctl), l, str.encode('gbk', 'replace')
		last.append((ctl, str))
		p += 2*l
		if ctl in CTL_HEAD_SET: p += 2
	if last:
		flushitem(last)
		last = []
	postbody()
	p = buf.find(BEGINMAGIC, q)
	first = False

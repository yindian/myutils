#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os, re
import xml.etree.cElementTree as ET
import pprint, pdb

def _basenode2base(node):
	if node.tag == 'string':
		data = node.text
	elif node.tag == 'integer':
		data = int(node.text, 0)
	else:
		raise Exception('Unknown type ' + node.tag)
	return data

def _listtree2list(tree):
	assert tree.tag == 'array'
	l = []
	for node in tree:
		if node.tag == 'array':
			data = _listtree2list(node)
		elif node.tag == 'dict':
			data = _dicttree2dict(node)
		else:
			data = _basenode2base(node)
		l.append(data)
	return l

def _dicttree2dict(tree):
	assert tree.tag == 'dict'
	d = {}
	lastkey = None
	for node in tree:
		if node.tag == 'key':
			lastkey = node.text
		else:
			assert lastkey
			if node.tag == 'dict':
				data = _dicttree2dict(node)
			elif node.tag == 'array':
				data = _listtree2list(node)
			else:
				data = _basenode2base(node)
			d[lastkey] = data
			lastkey = None
	return d

def xml2obj(xmlstr):
	tree = ET.fromstring(xmlstr)
	assert tree.tag == 'plist'
	assert len(tree) == 1
	node = tree[0]
	if node.tag == 'dict':
		data = _dicttree2dict(node)
	elif node.tag == 'array':
		data = _listtree2list(node)
	else:
		data = _basenode2base(node)
	return data

def numsortcmp(a, b):
	p = 0
	l = min(len(a), len(b))
	while p < l and a[p] == b[p]:
		p += 1
	if (p > 0 and a[p-1].isdigit()) or (p < l and a[p].isdigit() and 
			b[p].isdigit()):
		q = r = p
		while q < len(a) and a[q].isdigit():
			q += 1
		while r < len(b) and b[r].isdigit():
			r += 1
		while p > 0 and a[p-1].isdigit():
			p -= 1
		num1 = int(a[p:q])
		num2 = int(b[p:r])
		if num1 < num2:
			return -1
		elif num1 > num2:
			return 1
	return cmp(a, b)

def lstrip(s, f):
	p = 0
	l = len(s)
	while p < l and f(s[p]):
		p += 1
	return s[p:]

def getword(wordidx, d={}):
	fileidx = wordidx / 2500 + 1
	if not d.has_key(fileidx):
		f = open('str''ingIn''dex_%d.dat' % (fileidx,), 'rb')
		d[fileidx] = f.read().decode('utf-16le')[1:].splitlines()
		f.close()
	return d[fileidx][wordidx % 2500]

def getruby(wordidx, d={}):
	fileidx = wordidx / 2500 + 1
	if not d.has_key(fileidx):
		f = open('str''ingR''uby_%d.dat' % (fileidx,), 'rb')
		d[fileidx] = f.read().decode('utf-16le')[1:].splitlines()
		f.close()
	return d[fileidx][wordidx % 2500]

def getwordruby(wordidx, d={}):
	fileidx = wordidx / 1000
	if not d.has_key(fileidx):
		f = open('in''dex_%d.plist' % (fileidx,), 'rb')
		d[fileidx] = xml2obj(f.read())
		f.close()
	return d[fileidx][wordidx % 1000]

def getmeaning(wordidx, d={}):
	fileidx = wordidx / 1000
	if not d.has_key(fileidx):
		f = open('im''i_''h_%d.plist' % (fileidx,), 'rb')
		d[fileidx] = xml2obj(f.read())
		f.close()
	return d[fileidx][wordidx % 1000].rstrip()

def formatnonble(data):
	ar = data.split('$')
	result = [ar[0].replace('\n', '').replace(u'\ufe35',
			u'（').replace(u'\ufe36', u'）').replace(u'\ufe41',
				u'「').replace(u'\ufe42' , u'」')]
	right = False
	for i in xrange(1, len(ar)):
		if ar[i][0] == 'b':
			assert not right
			result.append('<b>')
		elif ar[i][0] == 'n':
			assert not right
			result.append('</b>')
		elif ar[i][0] == 'r':
			result.append('<br>')
			if not right:
				result.append('<indent val="4">')
				right = True
		else:
			raise(Exception('Unknown directive $' + ar[i][0]))
		result.append(ar[i][1:].replace('\n', '').replace(u'\ufe35',
			u'（').replace(u'\ufe36', u'）').replace(u'\ufe41',
				u'「').replace(u'\ufe42' , u'」'))
			
	return formatruby(''.join(result))

def getnonble(wordidx, gettype=0, l=[], d={}):
	if not l:
		f = open('non''ble.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		f = open('word''Data.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		writehtml = True
	else:
		writehtml = False
	if l[1].has_key(getword(wordidx)):
		key = getword(wordidx).encode('utf-8').encode('base64')
	else:
		key = l[0][wordidx]
	if writehtml:
		f = open('mei.htm', 'w')
		print >> f, '<html>\n<body>'
		for k, v in l[1].iteritems():
			try:
				int(k)
			except:
				k = k.encode('utf-8').encode('base64')
			print >> f, '<p><div id="%s"><indent val="0">' % (k,)
			print >> f, enc(formatnonble(v))
			print >> f, '</div><br></p><br>'
		print >> f, '</body>\n</html>'
		f.close()
	if gettype:
		return key
	return formatnonble(l[1][key])

indentpat = re.compile(r'&[0-9]+&')
warichupat = re.compile(r'\{(.*?)\}')
def formatmeaning(s, word, wordidx):
	s = indentpat.sub('', s)
	s = ''.join(s.splitlines())
	s = s.replace(u'\u2015', '<b>%s</b>' % (word,))
	s = warichupat.sub(r'<sub>\g<1></sub>', s)
	ar = s.split(u'｛')
	result = [ar[0]]
	for i in xrange(1, len(ar)):
		p = ar[i].index(u'｝')
		fn = ar[i][:p]
		if fn.startswith('mei'):
			result.append('<a href="mei.htm#%s">' % (
				getnonble(wordidx, 1)))
		result.append('<img src="')
		result.append(fn)
		if fn.startswith('G'):
			result.append('_16')
			if not os.path.exists(fn + '_16.png'):
				result.append('_s')
		result.append('.bmp" class="inline">')
		if fn.startswith('mei'):
			result.append('</a>')
		result.append(ar[i][p+1:])
	return ''.join(result)

def formatruby(s, d={}):
	if d.has_key(s):
		return d[s]
	ar = s.split('{')
	result = [ar[0]]
	for i in xrange(1,len(ar)):
		s = ar[i]
		p = s.find('}')
		if p > 0 and s.find(':', 0, p) > 0:
			q = s.find(':', 0, p)
			result.append('<ruby><rb>')
			result.append(s[:q])
			result.append('</rb><rt>')
			result.append(s[q+1:p])
			result.append('</rt></ruby>')
			result.append(s[p+1:])
		else:
			result.append('{')
			result.append(s)
	d[s] = ''.join(result)
	return d[s]

assert __name__ == '__main__'

f = open('gen''reD''ata.plist', 'r')
genredict = xml2obj(f.read())
f.close()

f = open('gen''reR''ubyL''ist.plist', 'r')
gruby = xml2obj(f.read())
f.close()
for g in gruby.keys():
	if g.endswith(u'\u9aef'):
		gg = g.replace(u'\u9aef', u'\u9ae5')
		if not gruby.has_key(gg):
			gruby[gg] = gruby[g].replace(u'\u9aef', u'\u9ae5')

of = open('out.htm', 'w')
print >> of, """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

vartbl = {
		0xff0d: 0x221c,
		0xff5e: 0x301c,
		0xffe0: 0xa2,
		0xffe1: 0xa3,
		}
enc = lambda s: s.translate(vartbl).encode('sjis','xmlcharrefreplace')

genrelist = []
for key1 in sorted(genredict.iterkeys(), cmp=numsortcmp):
	genre = lstrip(key1, lambda c: c.isupper())
	id1 = str(key1[:-len(genre)])
	subgenredict = genredict[key1]
	subs = []
	for key2 in sorted(subgenredict.iterkeys(), cmp=numsortcmp):
		subggenre = lstrip(key2, lambda c: c.isupper() or c.isdigit())
		id2 = str(key2[:-len(subggenre)])
		subsubgenredict = subgenredict[key2]
		subsubs = []
		for key3 in sorted(subsubgenredict.iterkeys(), cmp=numsortcmp):
			subsubggenre = lstrip(key3, lambda c: c.islower())
			id3 = str(key2[:-len(subggenre)] +
					key3[:-len(subsubggenre)])
			finaldict = subsubgenredict[key3]
			finals = []
			for key4 in sorted(finaldict.iterkeys(), numsortcmp):
				finalgenre = lstrip(key4, lambda c: c.isdigit())
				id4 = '@'+str(key4[:-len(finalgenre)])
				words = []
				for wordidx in finaldict[key4]:
					titletext = formatruby(
							getwordruby(
								wordidx)
							)
					print >> of, '<dt id="%d">%s</dt>' % (
							wordidx,
							enc(titletext)
							)
					word = getword(wordidx)
					if word != titletext:
						titletext.index('<ruby>')
						print >> of, '<key type="表記">%s</key>' % ( enc(word),)
						print >> of, '<key type="かな">%s</key>' % ( enc(getruby(wordidx)),)
					print >> of, '<dd>&nbsp;&nbsp;<a href="toc.htm#%s">↑</a>&nbsp;<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a><br><indent val="1">%s</dd>' % (
							'_'+`wordidx`,
							id1, enc(genre),
							id2, enc(subggenre),
							id3, enc(subsubggenre),
							id4, enc(finalgenre),
							enc(formatmeaning(
								getmeaning(
									wordidx)
								, word, wordidx
								)),)
					words.append((wordidx, titletext))
				finals.append((id4, finalgenre, words))
			subsubs.append((id3, subsubggenre, finals))
		subs.append((id2, subggenre, subsubs))
	genrelist.append((id1, genre, subs))

tf = open('toc.htm', 'w')
print >> tf, '<html>\n<body>'
print >> tf, '<p>'
for iden, genre, subs in genrelist:
	print >> tf, '<div id="%s"><a href="%s">%s</a><br></div>' % (
			'_'+iden, iden, enc(formatruby(gruby[genre])))
print >> tf, '</p>'
for iden, genre, subs in genrelist:
	print >> tf, '<h1 id="%s">%s</h1>' % (
			iden, enc(formatruby(gruby[genre])))
	print >> tf, '<p>'
	for subiden, subgenre, subsubs in subs:
		print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
				'_'+subiden,
				subiden, enc(formatruby(gruby[subgenre])),
				'_'+iden)
	print >> tf, '</p>'
	for subiden, subgenre, subsubs in subs:
		print >> tf, '<h2 id="%s">%s</h2>' % (subiden,
				enc(formatruby(gruby[subgenre])))
		print >> tf, '<p>'
		for subsubiden, subsubgenre, finals in subsubs:
			print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
					'_'+subsubiden,
					subsubiden,
					enc(formatruby(gruby[subsubgenre])),
					'_'+subiden)
		print >> tf, '</p>'
		for subsubiden, subsubgenre, finals in subsubs:
			print >> tf, '<h3 id="%s">%s</h2>' % (
					subsubiden,
					enc(formatruby(gruby[subsubgenre])))
			print >> tf, '<p>'
			for finaliden, finalgenre, words in finals:
				print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
						'_'+finaliden,
						finaliden,
						enc(formatruby(gruby[finalgenre])),
						'_'+subsubiden)
			print >> tf, '</p>'
			for finaliden, finalgenre, words in finals:
				print >> tf, '<h4 id="%s">%s</h2>' % (
						finaliden,
						enc(formatruby(gruby[finalgenre])))
				print >> tf, '<p>'
				for wordidx, word in words:
					print >> tf, '<div id="%s"><a href="out.htm#%s">%s</a> <a href="%s">↑</a><br></div>' % (
							'_'+`wordidx`,
							`wordidx`,
							enc(word),
							'_'+finaliden)
				print >> tf, '</p>'
print >> tf, '</body>\n</html>'

print >> of, """\
</dl>
</body>
</html>"""

of.close()
tf.close()

gaijiset = set()
f = open('out.htm', 'r')
for line in f:
	ar = line.split('&#')
	for i in xrange(1, len(ar)):
		p = ar[i].index(';')
		if ar[i].startswith('x'):
			code = int(ar[i][1:p], 16)
		else:
			code = int(ar[i][:p])
		gaijiset.add(code)
f = open('mei.htm', 'r')
for line in f:
	ar = line.split('&#')
	for i in xrange(1, len(ar)):
		p = ar[i].index(';')
		if ar[i].startswith('x'):
			code = int(ar[i][1:p], 16)
		else:
			code = int(ar[i][:p])
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

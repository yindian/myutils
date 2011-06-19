#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os, re
import xml.etree.cElementTree as ET
import pprint, pdb

# preparations: 1. convert plist to xml. 2. convert png to bmp (no alpha)

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

def v2h(s):
	return s.replace(u'\ufe35', u'（').replace(u'\ufe36', u'）'
			).replace(u'\ufe41', u'「').replace(u'\ufe42' , u'」'
					).replace(u'\ufe43', u'『').replace(
							u'\ufe44', u'』')

def formatnonble(data):
	ar = data.split('$')
	result = [v2h(ar[0].replace('\n', ''))]
	right = False
	rightlines = []
	for i in xrange(1, len(ar)):
		if ar[i][0] == 'b':
			assert not right
			result.append('<b>')
			result.append(v2h(ar[i][1:].replace('\n', '')))
		elif ar[i][0] == 'n':
			assert not right
			result.append('</b>')
			result.append(v2h(ar[i][1:].replace('\n', '')))
		elif ar[i][0] == 'r':
			if not right:
				right = True
			rightlines.append(v2h(ar[i][1:].replace('\n', '')))
		else:
			raise(Exception('Unknown directive $' + ar[i][0]))
	if right:
		l = max(10, *map(len, rightlines))
		for s in rightlines:
			if s:
				result.append('<br>\n')
				result.append('<indent val="%d">' % (l-len(s)))
				result.append(s)
	return formatruby(''.join(result))

def getnonble(wordidx, gettype=0, l=[]):
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
		key = getword(wordidx).encode('utf-8').encode('base64').rstrip()
	else:
		key = l[0][wordidx]
	if writehtml:
		f = open('mei.htm', 'w')
		print >> f, '<html>\n<body>'
		for k, v in l[1].iteritems():
			try:
				int(k)
			except:
				k = k.encode('utf-8').encode('base64').rstrip()
			print >> f, '<p><div id="%s"><indent val="0">' % (k,)
			print >> f, enc(formatnonble(v))
			print >> f, '</div><br></p><br>'
		print >> f, '</body>\n</html>'
		f.close()
	if gettype:
		return key
	return formatnonble(l[1][key])

def getnuance(wordidx, keyidx=0, l=[]):
	if not l:
		f = open('nuan''ceL''istH.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		f = open('nuan''ceDa''taH.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		writehtml = True
	else:
		writehtml = False
	key = l[0][wordidx].split('/')
	if writehtml:
		f = open('san.htm', 'w')
		print >> f, '<html>\n<body>\n<dl>'
		for k, v in l[1].iteritems():
			print >> f, '<dt id="%s" noindex="1">%s</dt><br>\n<dd><indent val="1">' % (
					k.encode('utf-8').encode('base64'
						).rstrip(),
					enc(warichupat.sub(r'<sub>\g<1></sub>',
						k)))
			print >> f, enc(warichupat.sub(r'<sub>\g<1></sub>',
						v.replace('\n', '')))
			print >> f, '</dd><br>'
		print >> f, '</dl>\n</body>\n</html>'
		f.close()
	return key[keyidx].encode('utf-8').encode('base64').rstrip()

def getimage(wordidx, keyidx=0, l=[]):
	if not l:
		f = open('im''ageD''ata.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		f = open('im''age''Info.plist', 'r')
		l.append(xml2obj(f.read()))
		f.close()
		writehtml = True
	else:
		writehtml = False
	key = l[0][wordidx][keyidx]['im''age''Name']
	if writehtml:
		f = open('zu.htm', 'w')
		print >> f, '<html>\n<body>\n<dl>'
		for k, v in l[1].iteritems():
			print >> f, '<dt id="%s" noindex="1">%s</dt>\n<dd><indent val="1">' % (
					k,
					enc(v['im''age''Title']))
			gentxtimg(k, v['title''List'])
			print >> f, '<img src="%s.bmp">' % (k,)
			print >> f, '</dd>\n<X4081>1F03 1F02</X4081>'
		print >> f, '</dl>\n</body>\n</html>'
		f.close()
	return key

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
		elif fn.startswith('sar'):
			try:
				keyidx = int(fn[6]) - 1
			except:
				keyidx = 0
			result.append('<a href="san.htm#%s">' % (
				getnuance(wordidx, keyidx)))
		elif fn.startswith('zu'):
			try:
				keyidx = int(fn[2]) - 1
			except:
				keyidx = 0
			result.append('<a href="zu.htm#%s">' % (
				getimage(wordidx, keyidx)))
		result.append('<img src="')
		result.append(fn)
		if fn.startswith('G'):
			result.append('_16')
			if not os.path.exists(fn + '_16.png'):
				result.append('_s')
		result.append('.bmp" class="inline">')
		if fn.startswith('mei') or fn.startswith('sar'
				) or fn.startswith('zu'):
			result.append('</a>')
		result.append(ar[i][p+1:])
	return ''.join(result)

def gettypes(wordidx):
	s = getmeaning(wordidx)
	s = indentpat.sub('', s)
	s = ''.join(s.splitlines())
	ar = s.split(u'｛')
	result = []
	for i in xrange(1, len(ar)):
		p = ar[i].index(u'｝')
		fn = ar[i][:p]
		if fn.startswith('bun'):
			result.append('文章')
		elif fn.startswith('kai'):
			result.append('会話')
		elif fn.startswith('koh'):
			result.append('古風')
		elif fn.startswith('zok'):
			result.append('俗語')
		elif fn.startswith('shi'):
			result.append('新年')
		elif fn.startswith('har'):
			result.append('春')
		elif fn.startswith('nat'):
			result.append('夏')
		elif fn.startswith('aki'):
			result.append('秋')
		elif fn.startswith('huy'):
			result.append('冬')
	return result

def getextra(wordidx):
	s = getmeaning(wordidx)
	s = indentpat.sub('', s)
	s = ''.join(s.splitlines())
	ar = s.split(u'｛')
	result = []
	for i in xrange(1, len(ar)):
		p = ar[i].index(u'｝')
		fn = ar[i][:p]
		if fn.startswith('mei'):
			result.append('名言・名文')
		elif fn.startswith('sar'):
			result.append('類語のニュアンス')
		elif fn.startswith('zu'):
			result.append('イラスト')
	return list(set(result))

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

def yomi(s, d={}):
	s = gruby[s]
	if d.has_key(s):
		return d[s]
	ar = s.split('{')
	result = [ar[0]]
	for i in xrange(1,len(ar)):
		s = ar[i]
		p = s.find('}')
		if p > 0 and s.find(':', 0, p) > 0:
			q = s.find(':', 0, p)
			result.append(s[q+1:p])
			result.append(s[p+1:])
		else:
			result.append('{')
			result.append(s)
	d[s] = ''.join(result)
	return d[s]

def kanji(c):
	try:
		c.encode('sjis')
		return 0x4E00 <= ord(c) <= 0x9FA5
	except:
		return False

from PIL import ImageFont, Image, ImageDraw
font1 = ImageFont.truetype('ipag.ttc', 56, index=1)
font2 = ImageFont.truetype('ipag.ttc', 28, index=1)
font3 = ImageFont.truetype('GoPr6N.otf', 28)
def genpic(text, haspic=set()):
	fname = enc(text).encode('hex') + '.bmp'
	if not fname in haspic:
		font = font1
		size = font.getsize(text)
		img = Image.new("RGB", size, (255,255,255))
		draw = ImageDraw.Draw(img)
		draw.text((0,0), text, (0,0,0), font=font)
		img = img.resize(tuple([x/4 for x in size]), Image.ANTIALIAS)
		img.save(fname)
		haspic.add(fname)
	return '<img src="%s" class="inline">' % (fname,)

def gentxtimg(base, text, haspic=set()):
	if base in haspic:
		return
	img = Image.open(base + '.png')
	try:
		img = img.convert("RGB")
	except:
		return
	draw = ImageDraw.Draw(img)
	for d in text:
		s, x, y = map(d.get, ('title', 'x', 'y'))
		if s and (x or y):
			for l in s.splitlines():
				try:
					l.encode('sjis')
					draw.text((x,y), l, (0,0,0), font=font2)
					font = font2
				except:
					draw.text((x,y), l, (0,0,0), font=font3)
					font = font3
				y += font.getsize(l)[1] + 1
	img.save(base + '.bmp') # need convert to palette bmp afterwards
	haspic.add(base)

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
					for c in filter(kanji, word):
						print >> of, '<key type="クロス">%s</key>' % ( enc(c),)
					print >> of, '<key type="複合" name="分類体系">%s</key>' % ( enc(genre),)
					print >> of, '<key type="複合" name="分類体系2">%s</key>' % ( enc(subggenre),)
					print >> of, '<key type="複合" name="絞り込み">見出し</key>'
					for s in gettypes(wordidx):
						print >> of, '<key type="複合" name="絞り込み">%s</key>' % (s,)
						print >> of, '<key type="複合" name="絞り込み1">%s</key>' % (s,)
						print >> of, '<key type="複合" name="絞り込み2">%s</key>' % (s,)
						print >> of, '<key type="複合" name="絞り込み3">%s</key>' % (s,)
						print >> of, '<key type="複合" name="絞り込み4">%s</key>' % (s,)
						print >> of, '<key type="複合" name="絞込み">%s</key>' % (s,)
					for s in getextra(wordidx):
						print >> of, '<key type="複合" name="データ1">%s</key>' % (s,)
						print >> of, '<key type="複合" name="データ2">%s</key>' % (s,)
					print >> of, '<dd>&nbsp;&nbsp;<a href="toc.htm#%s">↑</a>&nbsp;<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a>≫<a href="toc.htm#%s">%s</a><br><indent val="1">%s</dd>' % (
							'_'+`wordidx`,
							id1, genpic(genre),
							id2, genpic(subggenre),
							id3, genpic(subsubggenre),
							id4, genpic(finalgenre),
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
	print >> tf, '<h1 id="%s" noindex="1">%s</h1>' % (
			iden, enc(formatruby(gruby[genre])))
	print >> tf, '<key type="条件">%s</key>' % (enc(genre),)
	print >> tf, '<key type="条件">%s</key>' % (enc(yomi(genre)),)
	print >> tf, '<p>'
	for subiden, subgenre, subsubs in subs:
		print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
				'_'+subiden,
				subiden, enc(formatruby(gruby[subgenre])),
				'_'+iden)
	print >> tf, '</p>'
	for subiden, subgenre, subsubs in subs:
		print >> tf, '<h2 id="%s" noindex="1">%s</h2>' % (subiden,
				enc(formatruby(gruby[subgenre])))
		print >> tf, '<key type="条件">%s</key>' % (enc(subgenre),)
		print >> tf, '<key type="条件">%s</key>' % (enc(yomi(subgenre)),)
		for c in filter(kanji, subgenre):
			print >> tf, '<key type="クロス">%s</key>' % ( enc(c),)
		print >> tf, '<key type="複合" name="分類体系">%s</key>' % ( enc(genre),)
		print >> tf, '<p>'
		for subsubiden, subsubgenre, finals in subsubs:
			print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
					'_'+subsubiden,
					subsubiden,
					enc(formatruby(gruby[subsubgenre])),
					'_'+subiden)
		print >> tf, '</p>'
		for subsubiden, subsubgenre, finals in subsubs:
			print >> tf, '<h3 id="%s" noindex="1">%s</h2>' % (
					subsubiden,
					enc(formatruby(gruby[subsubgenre])))
			print >> tf, '<key type="条件">%s</key>' % (enc(subsubgenre),)
			print >> tf, '<key type="条件">%s</key>' % (enc(yomi(subsubgenre)),)
			for c in filter(kanji, subsubgenre):
				print >> tf, '<key type="クロス">%s</key>' % ( enc(c),)
			print >> tf, '<key type="複合" name="分類体系">%s</key>' % ( enc(genre),)
			print >> tf, '<key type="複合" name="分類体系2">%s</key>' % ( enc(subgenre),)
			print >> tf, '<p>'
			for finaliden, finalgenre, words in finals:
				print >> tf, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
						'_'+finaliden,
						finaliden,
						enc(formatruby(gruby[finalgenre])),
						'_'+subsubiden)
			print >> tf, '</p>'
			for finaliden, finalgenre, words in finals:
				print >> tf, '<h4 id="%s" noindex="1">%s</h2>' % (
						finaliden,
						enc(formatruby(gruby[finalgenre])))
				print >> tf, '<key type="条件">%s</key>' % (enc(finalgenre),)
				print >> tf, '<key type="条件">%s</key>' % (enc(yomi(finalgenre)),)
				for c in filter(kanji, finalgenre):
					print >> tf, '<key type="クロス">%s</key>' % ( enc(c),)
				print >> tf, '<key type="複合" name="分類体系">%s</key>' % ( enc(genre),)
				print >> tf, '<key type="複合" name="分類体系2">%s</key>' % ( enc(subgenre),)
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

cf = open('cplx.xml', 'w')
print >> cf, '<?xml version="1.0" encoding="Shift_JIS"?>'
print >> cf, '<complex>'
print >> cf, '<group name="分類検索">'
print >> cf, '<category name="分類体系">'
for iden, genre, subs in genrelist:
	print >> cf, '<subcategory name="%s">' % (enc(genre),)
print >> cf, '</category>'
print >> cf, '<category name="分類体系2">'
for iden, genre, subs in genrelist:
	print >> cf, '<subcategory name="%s">' % (enc(genre),)
	for subiden, subgenre, subsubs in subs:
		print >> cf, '<subcategory name="%s" />' % (enc(subgenre),)
	print >> cf, '</subcategory>'
print >> cf, '</category>'
print >> cf, '<category name="絞り込み">'
for s in u'見出し 文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<keyword name="キーワード1" />'
print >> cf, '<keyword name="キーワード2" />'
print >> cf, '</group>'
print >> cf, '<group name="絞込検索">'
print >> cf, '<category name="絞り込み1">'
for s in u'文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<category name="絞り込み2">'
for s in u'文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<category name="絞り込み3">'
for s in u'文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<category name="絞り込み4">'
for s in u'文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<keyword name="キーワード" />'
print >> cf, '</group>'
print >> cf, '<group name="エキストラ">'
print >> cf, '<category name="データ1">'
for s in u'名言・名文 イラスト 類語のニュアンス'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<category name="データ2">'
for s in u'名言・名文 イラスト 類語のニュアンス'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<category name="絞込み">'
for s in u'文章 会話 古風 俗語 新年 春 夏 秋 冬'.split():
	print >> cf, '<subcategory name="%s" />' % (enc(s),)
print >> cf, '</category>'
print >> cf, '<keyword name="キーワード" />'
print >> cf, '</group>'
print >> cf, '</complex>'
cf.close()

gaijiset = set()
for fn in ('out.htm', 'mei.htm', 'san.htm', 'zu.htm'):
	f = open(fn, 'r')
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

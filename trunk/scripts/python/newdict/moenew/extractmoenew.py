#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob
import libxml2dom
import pdb, traceback
fencoding = 'big5-hkscs'
outenc = 'gbk'
DEBUG = True

getindex = re.compile(r'href="([^"]*)"')
getword = re.compile(ur'\u3010(.*?)\u3011')
getword2 = re.compile(r'<?FE50>(.*?)<?FE51>')
tsemuk = unicode(u'\u8a5e\u76ee'.encode(fencoding), 'latin-1')
chusik = unicode(u'\u6ce8\u91cb'.encode(fencoding), 'latin-1')

getinvcode = re.compile(r"can't decode bytes in position (\d*)-(\d*):")

def genmoedict(result, dirname, fnames):
	indexfile = os.path.join(dirname, 'index.html')
	assert os.path.exists(indexfile)
	f = open(indexfile, 'r')
	buf = f.read()
	try:
		assert buf.find('</html>') > 0
	except:
		print >> sys.stderr, 'Error: incomplete index.html under ', dirname
	finally:
		flist = getindex.findall(buf)[1:]
	f.close()
	for fname in flist:
		isdir = False
		if fname[-1] == '/':
			fname = fname[:-1]
			isdir = True
		elif fname.find('/') > 0:
			p = fname.find('/')
			if fname[p+1:] == 'index.html':
				fname = fname[:p]
				isdir = True
		if fname not in fnames:
			print >> sys.stderr, 'Warning: %s not in %s' % (
					fname, dirname)
			continue
		if isdir: continue
		if not (fname.startswith('s_') and fname.endswith('.html')):
			print >> sys.stderr, 'Ignoring ' + fname
			continue
		num = int(fname[2:-5])
		try:
			f = open(os.path.join(dirname, fname), 'r')
			buf = f.read()
			f.close()
		except:
			print >> sys.stderr, 'Error reading %s under %s' % (
					fname, dirname)
			continue
		try:
			doc = libxml2dom.parseString(buf, html=1, 
					htmlencoding='latin-1')
		except:
			print >> sys.stderr, 'Error parsing %s under %s' % (
					fname, dirname)
			continue
		try:
			result.append((num, getwordmeanfromdoc(doc)))
		except:
			print >> sys.stderr, 'Error processing %s under %s' % (
					fname, dirname)
			if DEBUG:
				traceback.print_exc()
				pdb.set_trace()
			raise

def getwordmeanfromdoc(doc):
	word = mean = None
	body = doc.getElementsByTagName('tbody')
	assert len(body) == 1
	#print body[0].textContent.encode('latin-1')
	table = body[0].getElementsByTagName('table')
	try:
		assert len(table) == 1
	except:
		assert table[1].textContent.startswith(u'\xb9\xcf')
	table = table[0]
	node = table.firstChild
	assert node.nodeType == node.ELEMENT_NODE
	assert node.nodeName == 'tr'
	assert len(node.childNodes) == 2
	assert node.firstChild.textContent == tsemuk
	word = node2text(node.childNodes[1])
	try:
		word = unicode(word.encode('latin-1'), fencoding)
	except:
		print >> sys.stderr, 'Error decoding word %s' % (unicode(
			word.encode('latin-1'), fencoding, 'replace').encode(
				outenc, 'replace'),)
		raise
	words = getword.findall(word)
	try:
		assert len(words) == 1
	except:
		words = getword2.findall(word)
		assert len(words) == 1
	word = words[0]
	#print word.encode(outenc, 'replace')
	mean = []
	for child in table.childNodes:
		if child.nodeType == node.TEXT_NODE:
			assert not child.nodeValue.strip()
			continue
		else:
			assert child.nodeName == 'tr'
			try:
				assert len(child.childNodes)==2
			except:
				assert not child.textContent
				continue
			item = child.childNodes[0].textContent
			mean.append(item)
			if item != chusik:
				mean.append(': ')
				mean.append(node2text(child.childNodes[1]))
			else:
				mean.append(':\n')
				node = child.childNodes[1].firstChild
				assert node.nodeName == 'pre'
				mean.append(node2text(node))
			mean.append('\n')
	mean = ''.join(mean)
	try:
		mean = unicode(mean.encode('latin-1'), fencoding)
	except UnicodeDecodeError, e:
		print >> sys.stderr, e
		codes = getinvcode.findall(str(e))
		assert len(codes) == 1
		st, ed = map(int, codes[0])
		print >> sys.stderr, 'Invalid character %s for'%`mean[st:ed+1]`, 
		print >> sys.stderr, unicode(
				mean[:mean.index('\n')].encode('latin-1'),
				fencoding).encode(outenc, 'replace')
		mean = unicode(mean.encode('latin-1'), fencoding, 'replace')
	return word, mean

def node2text(node):
	result = []
	for child in node.childNodes:
		if child.nodeType == child.TEXT_NODE:
			result.append(child.nodeValue)
		elif child.nodeName in ('a', 'embed'):
			assert child.textContent.strip() == ''
		elif child.nodeName == 'table':
			text = child.textContent
			assert text.startswith(u'\xb9\xcf')
			images = child.getElementsByTagName('img')
			assert len(images) >= 1
			images = [i.getAttribute('src') for i in images]
			result.extend(['\n[?%s]' % i for i in images])
		else:
			try:
				assert child.nodeName == 'img'
			except:
				print >>sys.stderr,child.nodeType,child.nodeName
				raise
			img = child.getAttribute('src')
			p = img.find('Tfonts/')
			if p >= 0:
				img = img[p+7:]
			try:
				assert img.endswith('._104_0.gif')
			except:
				if img.endswith('gif_04.gif'):
					continue
				print >> sys.stderr, img
				raise
			img = img[:-11]
			result.append('<?%s>' % (img))
	return ''.join(result)

result = []
os.path.walk('.', genmoedict, result)
result = filter(None, result)
result.sort()
result = [b for a, b in result]

for word, mean in result:
	sys.stdout.write(word.encode('utf-8'))
	sys.stdout.write('\t')
	sys.stdout.write(mean.replace('\n', '\\n').encode('utf-8'))
	sys.stdout.write('\n')

print >> sys.stderr, 'Done'

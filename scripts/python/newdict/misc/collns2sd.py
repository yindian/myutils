#!/usr/bin/env python
import sys
import glob
import re
from BeautifulSoup import BeautifulSoup
import pdb

#colpat = re.compile(r'<!--Collins[^>]*-->(.*?)<!--Collins End-->', re.S)
#colpat = re.compile(r'<!--Collins Start-->(.*?)<!--Collins End-->', re.S)
colpat = re.compile(r'^\s*<!--Collins Start-->(.*?)<!--Collins End-->', re.S | re.M)
spcpat = re.compile(r'''[ 	\r]+''')
spcpat2 = re.compile(r'\s+')
wordgrampat = re.compile(r'<div ([^>]*) id="word_gram[^>]*">')
wordhrefpat = re.compile(r'href="/([^"]*)"')
def ref2h(m):
	return 'href="bword://%s"' % (m.group(1).replace('_', ' '),)

def nodetext(node):
	return spcpat2.sub(u' ', u''.join(node.findAll(text=True)).replace(u'\u0080', u' ')).strip()

whole_line_tags = set([u'div', u'p', u'ul', u'ol', u'li', u'h1',\
		u'h2', u'h3', u'h4', u'h5', u'h6', u'dl', u'dt'])

def nodefmt(node, indent=0):
	try:
		node.contents
	except AttributeError:
		return unicode(node).replace(u'\u0080', u' ')
	result = []
	for sub in node.contents:
		text = nodefmt(sub, indent)
		if not text.strip():
			if text.find(u'\n') >= 0:
				text = u'\n'
			elif result and not result[-1][-1].isspace():
				result.append(u' ')
				continue
			elif not result or result[-1].endswith(u'\n'):
				continue
		elif not result or result[-1][-1].isspace():
			text = text.lstrip()
		if text == u'\n' and (not result or result[-1].endswith(u'\n')):
			pass
		elif text:
			if text != u'\n' and getattr(sub, 'name', None) in whole_line_tags and result and not result[-1].endswith(u'\n'):
				result[-1] = result[-1].rstrip()
				result.append(u'\n')
				text = text.lstrip()
			if text:
				result.append(text)
	result = u''.join(result)
	if node.name in whole_line_tags and not result.endswith(u'\n'):
		return result + u'\n'
	return result

def getmeaning(word, buf):
	result = []
	soup = BeautifulSoup(buf, convertEntities=BeautifulSoup.HTML_ENTITIES)
	part = 0
	for content in soup.find('div', 'part_main').findAll(True, recursive=False):
		if content.name == 'div':
			assert content['class'] == 'collins_content' or content['class'].rstrip() == 'collins_content'
			for node in content(True, recursive=False):
				assert node.name == 'div'
				if node['class'] == 'collins_en_cn':
					typ = node.div and node.div['class']
					if typ == 'caption':
						assert node.div.find(True).name == 'span'
					elif typ == 'caption about':
						assert node.div.find(True).name == 'dl'
					elif typ == 'en_tip':
						# SAT
						pass
					elif typ is None:
						# ('bit', 'bound', 'cut off')
						print >> sys.stderr, 'Possibly empty item in', fname
					else:
						raise Exception('Unknown class %s' % (typ,))
				elif node['class'] == 'vEn_tip':
					# account
					assert node.find(True).name == 'strong'
				elif node['class'] == 'vExplain_s':
					# get
					pass
				elif node['class'] == 'vExplain_r':
					# Christian Science
					pass
				else:
					raise Exception('Unknown class %s' % (node['class'],))
				result.append(spcpat.sub(u' ', nodefmt(node)))
		elif content.name == 'h3':
			part += 1
			result.append(u'<big><b>%d. %s</b></big>' % (part, nodetext(content),))
		else:
			raise Exception('Unknown tag %s' % (content.name,))
	return u'\n'.join(result)

assert __name__ == '__main__'

try:
	f = open('style.css')
except:
	f = open('../style.css')
style = '<style type="text/css">\n' + f.read() + '</style>\n'
f.close()
style = style.replace('\r\n', '\\n').replace('\n', '\\n')
flist = glob.glob('*')
#flist = glob.glob('www.iciba.com/get')
flist.sort()
result = []
for fname in flist:
	f = open(fname)
	buf = f.read()
	f.close()
	try:
		buf = colpat.findall(buf)[0]
	except:
		print >> sys.stderr, 'Not found in', fname
		continue
	result.append(fname)
	result.append('\t')
	#result.append(style)
	#buf = wordgrampat.sub('<div>', buf)
	#buf = wordhrefpat.sub(ref2h, buf)
	#result.append(spcpat.sub(' ', buf).replace('\n', '\\n'))

	try:
		result.append(getmeaning(fname, spcpat2.sub(' ', buf)).encode('utf-8').replace('\n', '\\n'))
	except:
		print >> sys.stderr, 'Error parsing', fname
		print BeautifulSoup(buf).prettify()
		raise
	result.append('\n')
print ''.join(result)

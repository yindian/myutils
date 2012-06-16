#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
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
	return spcpat2.sub(u' ', u''.join(node.findAll(text=True)).replace(u'\xa0', u' ')).strip()

def addbefore(text, what):
	p = 0
	l = len(text)
	while p < l:
		if text[p] == '<':
			p = text.index('>', p)
		elif not text[p].isspace():
			break
		p += 1
	return text[:p] + what + text[p:]

whole_line_tags = set([u'div', u'p', u'ul', u'ol', u'li', u'h1',\
		u'h2', u'h3', u'h4', u'h5', u'h6', u'dl', u'dt'])
keep_tags = set([u'abr', u'b', u'i', u'sub', u'sup', u'tt', u'big', u'small', u'tr', u'ex', u'k', u'c', u'rref', u'kref', u'iref'])

def nodefmt(node, indent=0):
	try:
		node.contents
	except AttributeError:
		return unicode(node).replace(u'\xa0', u' ')
	assert node.name != 'br'
	result = []
	for sub in node.contents:
		newindent = indent
		try:
			if sub.name == 'span' and sub['class'] == 'tips_box':
				newindent += 4
				sub.name = 'div'
			elif sub.name == 'li' and sub['class'].startswith('explain'):
				newindent += 3
		except:
			pass
		text = nodefmt(sub, newindent)
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
			#if text.startswith(u'【搭配模式】'):
			#	pdb.set_trace()
			if text != u'\n' and getattr(sub, 'name', None) in whole_line_tags and result and not result[-1].endswith(u'\n'):
				if node.name == u'span' and sub.name == u'div' and sub.get('class') == u'tips_main':
					t = text.strip()
					if t:
						text = u'(%s)' % (t,)
				else:
					result[-1] = result[-1].rstrip()
					result.append(u'\n')
					text = text.lstrip()
			if text:
				if newindent and (result and result[-1].endswith(u'\n')):
					text = addbefore(text, newindent * u'　')
				result.append(text)
	result = u''.join(result)
	if node.name == u'b':
		result = u'<c>%s</c>' % (result,)
	elif node.name == u'span':
		cls = node.get('class')
		if cls == u'text_blue':
			node.name = u'c'
		elif cls == u'num':
			result = u'<big>%s</big>' % (result,)
		elif cls == u'st' or cls == u'text_gray':
			try:
				node.get('style').index('bold')
			except:
				pass
			else:
				result = u'<b>%s</b>' % (result,)
	elif node.name == u'a':
		href = node['href']
		if href.startswith('/'):
			word = href[1:].replace('_', ' ')
			see = seealso = False
			if word.startswith('See'):
				assert result.startswith('See')
				word = ' '.join(word.split()[1:])
				assert word
				result = ' '.join(result.split()[1:])
				see = True
			elif word.startswith('see also'):
				assert result.startswith('see also')
				word = ' '.join(word.split()[2:])
				assert word
				result = ' '.join(result.split()[2:])
				seealso = True
			if word != result:
				print >> sys.stderr, 'Link mismatch: %s vs %s'%(
						word.encode('utf-8'), result.encode('utf-8'))
			result = u'<kref>%s</kref>' % (result,)
			if see:
				result = u'See ' + result
			elif seealso:
				result = u'see also ' + result
	elif node.name == u'li':
		try:
			assert node['class'].startswith('explain')
		except:
			ar = result.splitlines()
			try:
				assert len(ar) == 2
			except:
				assert len(ar) == 1
				result = u'<ex>　　・%s</ex>' % (ar[0], )
			else:
				result = u'<ex>　　・%s\n　　　%s</ex>' % (ar[0], ar[1])
		else:
			result = addbefore(result, u'◆')
	elif node.name == u'div':
		try:
			assert node['class'].startswith('explain')
		except:
			pass
		else:
			result = addbefore(result, u'◆')
	elif node.name == u'strong':
		result = u'<b><big>%s</big></b>' % (result,)
	if node.name in keep_tags:
		result = u'<%s>%s</%s>' % (node.name, result, node.name)
	if node.name in whole_line_tags and not result.endswith(u'\n'):
		return result + u'\n'
	return result

def getmeaning(word, buf):
	result = []
	soup = BeautifulSoup(buf, convertEntities=BeautifulSoup.HTML_ENTITIES,
			fromEncoding='utf-8')
	part = 0
	for content in reduce(lambda a, b: a + b, [div.findAll(True, recursive=False) for div in reduce(lambda a, b: a + [b], soup.findAll('div', 'part_main'), [])], []):
		if content.name == 'div':
			if pronfreqmap.has_key(word) and pronfreqmap[word][part]:
				result.append(u'　<tr>%s</tr> %s' % 
						pronfreqmap[word][part])
			assert content['class'].split()[0] == 'collins_content'
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
				result.append(nodefmt(node))
		elif content.name == 'h3':
			part += 1
			result.append(u'<big><b>%d. %s</b></big>' % (part, nodetext(content),))
		else:
			raise Exception('Unknown tag %s' % (content.name,))
	if pronfreqmap.has_key(word):
		try:
			assert len(pronfreqmap[word]) == part + 1
		except:
			print >> sys.stderr, 'Part number mismatch', fname
	return u'\n'.join(result)

assert __name__ == '__main__'

pronfreqmap = {}

if len(sys.argv) > 1:
	from romanclass import fromRoman
	f = open(sys.argv[1], 'rb')
	buf = f.read()
	f.close()
	buf = buf.decode('utf-16le')
	def flushpronfreq(word, pron, freq):
		if pron or freq:
			pronfreqmap.setdefault(word, []).append((pron,
				u'★' * (freq or 0)))
		else:
			pronfreqmap.setdefault(word, []).append(None)
	word = pron = freq = None
	checktr = False
	checkfreq = 0
	for line in buf.splitlines():
		if not line.startswith('\t'):
			if word is not None:
				flushpronfreq(word, pron, freq)
			word = line
			part = 0
			pron = freq = None
			checktr = True
			checkfreq = 3
		else:
			assert word
			if line.startswith('\t[b]'):
				flushpronfreq(word, pron, freq)
				p = line.index('[/b]')
				try:
					newpart = fromRoman(line[4:p])
				except:
					pass
				else:
					assert newpart == part + 1
					part = newpart
					pron = freq = None
					checktr = True
					checkfreq = 3
			if checktr:
				p = line.find('\\[[t]')
				if p > 0:
					q = line.find('[/t]\\]')
					pron = line[p+5:q]
				checktr = False
			if checkfreq:
				if line.startswith('\t[m1][p]'):
					n = line.count(u'♦')
					if n > 0:
						freq = n
				checkfreq -= 1
	if word is not None:
		flushpronfreq(word, pron, freq)

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
	fname = os.path.basename(fname)
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
	sys.stdout.writelines(result)
	result = []

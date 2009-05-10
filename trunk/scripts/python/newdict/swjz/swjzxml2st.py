#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob, pprint
import libxml2dom
from libxml2dom import Node

def char2utf8(code):
	if code < 0x10000:
		return unichr(code).encode('utf-8')
	else:
		assert code < 0x200000
		return ''.join(map(chr, [
			0xf0 | (code >> 18),
			0x80 | ((code >> 12) & 0x3f),
			0x80 | ((code >> 6) & 0x3f),
			0x80 | (code & 0x3f)]))
try:
	fnenc = 'utf-8'
	from ctypes import windll
	from ctypes.wintypes import DWORD
	STD_OUTPUT_HANDLE = DWORD(-11)
	STD_ERROR_HANDLE = DWORD(-12)
	GetStdHandle = windll.kernel32.GetStdHandle
	WriteConsoleW = windll.kernel32.WriteConsoleW

	def writeunicode(ustr, file=sys.stdout, newline=True):
		if file in (sys.stdout, sys.stderr) and file.isatty():
			which = file==sys.stdout and STD_OUTPUT_HANDLE or STD_ERROR_HANDLE;
			handle = GetStdHandle(which)
			if not isinstance(ustr, unicode):
				ustr = unicode(ustr)
			WriteConsoleW(handle, ustr, len(ustr), None, 0)
			if newline:
				print >> file
		else:
			if newline:
				print >> file, ustr.encode(fnenc, 'replace')
			else:
				file.write(ustr.encode(fnenc, 'replace'))
except:
	def writeunicode(ustr, file=sys.stdout, newline=True):
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

bigdict = []
bigkeys = []
hanzicount = 0

def insert(key, value, dic=bigdict, keys=bigkeys):
	if key in bigkeys:
		print >> sys.stderr, 'Warning: already has key ',
		writeunicode(key, sys.stderr)
	dic.append((key, value))
	keys.append(key)

def content2str(node):
	result = []
	for child in node.childNodes:
		if child.nodeType == Node.TEXT_NODE:
			result.append(child.nodeValue.replace('\n', '').strip())
		elif child.nodeType == Node.ELEMENT_NODE:
			assert child.nodeName == 'duan_note'
			result.append('(' + child.textContent + ')')
		else:
			raise Exception('Unexpected nodeType %d'%child.nodeType)
	return u''.join(result)

def section2str(node):
	assert node.nodeName == 'section'
	result = ['\n']
	for child in node.childNodes:
		if child.nodeType != Node.ELEMENT_NODE:
			continue
		if child.nodeName == 'section_num':
			result.append(child.textContent.strip())
			result.append('\n')
		elif child.nodeName == 'part_word':
			sub = child.childNodes
			assert sub[0].nodeName == 'wordhead'
			result.append('[')
			result.append(sub[0].textContent)
			result.append(']')
			assert sub[1].nodeType == Node.TEXT_NODE
			result.append(sub[1].value)
			if len(sub) > 2:
				assert len(sub) == 3
				assert sub[2].nodeName == 'duan_note'
				result.append('(')
				result.append(sub[2].textContent.strip())
				result.append(')')
			result.append('\n')
		else:
			raise Exception('Unexpected node ' + child.nodeName)
	return u''.join(result)

shuowenfct = {
		'explanation': lambda s: '['+s.textContent.strip()+']',
		'duan_note': lambda s: s.textContent.strip(),
		'section': section2str,
}

def shuowen2str(node):
	assert node.nodeName == 'shuowen'
	result = []
	last = None
	for child in node.childNodes:
		if child.nodeType != Node.ELEMENT_NODE:
			continue
		assert shuowenfct.has_key(child.nodeName)
		if last != 'section' and child.nodeName == 'section':
			result.append('\n')
		result.append(shuowenfct[child.nodeName](child))
		last = child.nodeName
	return u''.join(result)

def shuowenwordreg(node):
	assert node.nodeName == 'shuowen'
	word = None
	words = []
	means = []
	global hanzicount
	for child in node.childNodes:
		if child.nodeType != Node.ELEMENT_NODE:
			continue
		if child.nodeName == 'wordhead':
			if word is not None:
				mean = u''.join(result)
				#insert(word, mean)
				#hanzicount += 1
				means.append((word, mean))
			word = child.textContent.strip()
			result = []
			words.append(word)
			if child.firstChild.nodeName == 'img':
				img = child.firstChild.getAttribute('src')
				result.append(u'img:%s\n' % img)
		else:
			assert shuowenfct.has_key(child.nodeName)
			result.append(shuowenfct[child.nodeName](child))
	if word is not None:
		mean = u''.join(result)
		#insert(word, mean)
		#hanzicount += 1
		means.append((word, mean))
	hanzicount += 1
	if len(words) == 1:
		insert(*means[0])
	else:
		for word, mean in means:
			otherw = set(words)
			otherw.remove(word)
			word = '|'.join([word] + list(otherw))
			insert(word, mean)
	return u' '.join(words) + u'  '

assert __name__ == '__main__'

document = libxml2dom.parseString(open('swjz.xml', 'r').read());

assert document.lastChild.nodeName == 'book'
assert document.lastChild.childNodes[1].nodeName == 'volumes'

swjz = u'說文解字'

for child in document.lastChild.childNodes[1].childNodes:
	if child.nodeType != Node.ELEMENT_NODE:
		continue;
	if child.nodeName == 'preface':
		title = content = None
		for child2 in child.childNodes:
			if child2.nodeType != Node.ELEMENT_NODE:
				continue;
			if child2.nodeName == 'prefacetitle':
				title = child2.textContent.strip()
				if not title.startswith(swjz):
					title = swjz + u'注' + title
			elif child2.nodeName == 'content':
				assert title is not None
				content = content2str(child2)
				insert(title, content)
				title = content = None
		assert title is None and content is None
	elif child.nodeName == 'catalogs':
		pass
	elif child.nodeName == 'chapter':
		subnodes = filter(lambda s: s.nodeType == Node.ELEMENT_NODE,
				child.childNodes)
		assert subnodes[0].nodeName == 'chaptertitle'
		if subnodes[0].getAttribute('id') not in ('v29', 'v30'):
			sw2str = shuowenwordreg
		else:
			sw2str = shuowen2str
		title = content2str(subnodes[0])
		content = []
		last = None
		for child2 in subnodes[1:]:
			if not (last == child2.nodeName == 'shuowen'):
				content.append('\n')
			if child2.nodeName == 'shuowen':
				content.append(sw2str(child2))
			elif child2.nodeName == 'part_wordnum':
				content.append(content2str(child2))
				content.append('\n')
			else:
				content.append(child2.textContent.strip())
			last = child2.nodeName
		content = u''.join(content)
		insert(title, content)
	else:
		raise Exception('Unexpected node ' + child.nodeName)

print >> sys.stderr, 'Total Hanzi Count:', hanzicount

for key, value in bigdict:
	writeunicode(key, newline=False)
	print '\t',
	writeunicode(value.replace('\n', '\\n'))
	#writeunicode(key)
	#value = value.replace('[', '<big><font color="blue">').replace(']', '</font></big>')
	#value = value.splitlines()
	#if value[0].startswith('img'):
	#	value[0] = '<img src="%s.png">' % value[0][4:]
	#value = '<br>'.join(value)
	#writeunicode(value)
	#print

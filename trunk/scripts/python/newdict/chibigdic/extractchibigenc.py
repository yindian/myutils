#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob
import libxml2dom

whatfile = 'chi_big_enc/*'
outfile = 'o.out'
flushcnt = 1000
afterword = '----------'
afteritem = '=========='

namemap = {
		'u': u'\\u{%s}',
		'a': u'\\a{%s}',
		'strong': u'\\i{%s}',
		'div': u'\n%s',
		'span': u'%s',
}

def nodeToString(node):
	if not node:
		return u''
	if node.nodeType == node.TEXT_NODE:
		return node.nodeValue
	s = []
	for child in node.childNodes:
		if child.nodeType == child.TEXT_NODE:
			s.append(child.nodeValue.strip())
		else:
			s.append(namemap[child.nodeName] %(nodeToString(child)))
	if node.nodeName == 'div' and node.hasAttribute('style'):
		assert node.getAttribute('style').startswith('margin-left')
		s = [u'\\be{}'] + s + [u'\\ee{}']
	return u''.join(s)

def parseDiv(div):
	nodes = div.childNodes
	try:
		assert len(nodes) >= 2
	except:
		assert nodes[0].nodeName == 'span'
		print >> sys.stderr, 'Error: only one span tag found'
		return [], nodeToString(nodes[0])
	try:
		assert nodes[0].nodeType == nodes[0].TEXT_NODE
		assert nodes[0].nodeValue.strip() == ''
	except:
		print >> sys.stderr,'Warning: missing newline after div article'
		textnode = nodes[0].createTextNode(' ')
		nodes.insert(0, textnode)
	assert nodes[1].nodeType == nodes[1].ELEMENT_NODE
	result = []
	try:
		assert nodes[1].nodeName == 'span'
	except:
		assert nodes[1].nodeName == 'u'
		assert nodes[1].textContent[0] in 'IV'
		result.append('\\I{%s}\n' % (nodes[1].textContent))
		assert nodes[2].nodeType == nodes[2].TEXT_NODE
		del nodes[1:3]
	if not nodes[1].hasAttribute('class')and nodes[1].hasAttribute('style'):
		assert nodes[1].getAttribute('style').startswith('color:')
		synonyms = nodes[1].textContent.strip()
		if not (synonyms.startswith('(') and synonyms.endswith(')')):
			assert synonyms.startswith('(')
			p = 2
			while True:
				assert nodes[p].nodeType == nodes[p].TEXT_NODE
				p += 1
				assert nodes[p].nodeType== nodes[p].ELEMENT_NODE
				assert nodes[p].nodeName == 'span'
				assert nodes[p].getAttribute('style')[:3]=='col'
				synonyms += nodes[p-1].nodeValue.strip() + \
						nodes[p].textContent
				p += 1
				if synonyms.endswith(')'):
					break
			del nodes[2:p]
		assert synonyms.find('|') < 0
		synonyms = map(string.strip, synonyms[1:-1].split(','))
		result.append(u'(')
		result.append(u','.join(synonyms))
		result.append(u')\n')
		try:
			assert nodes[2].nodeType == nodes[2].TEXT_NODE
			assert nodes[2].nodeValue.strip() == ''
		except IndexError:
			print >> sys.stderr, 'Error: comment end after synonym'
			return synonyms, u''.join(result)
		del nodes[1:3]
		# for bt pages that have both reference and synonym
		if nodes[1].hasAttribute('style'):
			assert nodes[1].getAttribute('style').startswith(
					'color:')
			synonyms = nodes[1].textContent.strip()
			assert synonyms.startswith('(')
			assert synonyms.endswith(')')
			assert synonyms.find('|') < 0
			synonyms = map(string.strip, synonyms[1:-1].split(','))
			result.append(u'(')
			result.append(u','.join(synonyms))
			result.append(u')\n')
			assert nodes[2].nodeType == nodes[2].TEXT_NODE
			assert nodes[2].nodeValue.strip() == ''
			del nodes[1:3]
	else:
		synonyms = []
	if nodes[1].hasAttribute('class'):
		assert nodes[1].getAttribute('class') == 'dic_comment'
		comment = nodeToString(nodes[1])
	else:
		comment = u''
		nodes = [nodes[0]] * 3 + nodes[1:]
	if len(nodes) < 3:
		result.append(comment)
	else:
		assert nodes[2].nodeType == nodes[2].TEXT_NODE
		assert nodes[2].nodeValue.strip() == ''
		assert nodes[3].nodeType == nodes[3].ELEMENT_NODE
		try:
			assert nodes[3].nodeName == 'span'
		except:
			assert nodes[3].nodeName == 'u'
			nodes = nodes[:3] + [None, nodes[0]] + nodes[3:]
		result += [comment, nodeToString(nodes[3])]
		if len(nodes) > 4:
			p = 4
			result2 = []
			while p < len(nodes):
				assert nodes[p].nodeType == nodes[p].TEXT_NODE
				assert nodes[p].nodeValue.strip() == ''
				p += 1
				assert nodes[p].nodeType== nodes[p].ELEMENT_NODE
				assert nodes[p].nodeName == 'u'
				assert nodes[p].textContent[0] in 'IV'
				result2+= ['\n\\I{%s}\n'%(nodes[p].textContent)]
				p += 1
				assert nodes[p].nodeType == nodes[p].TEXT_NODE
				assert nodes[p].nodeValue.strip() == ''
				p += 1
				assert nodes[p].nodeType== nodes[p].ELEMENT_NODE
				assert nodes[p].nodeName == 'span'
				if nodes[p].hasAttribute('class'):
					assert nodes[p].getAttribute('class') \
							== 'dic_comment'
					comment = nodeToString(nodes[p])
					result2.append(comment)
				else:
					p -= 2
				p += 1
				if p >= len(nodes):
					break
				assert nodes[p].nodeType == nodes[p].TEXT_NODE
				assert nodes[p].nodeValue.strip() == ''
				if p + 1 < len(nodes) and nodes[p+1].nodeName\
						== 'span':
					result2.append(nodeToString(nodes[p+1]))
					p += 2
			result += result2
	result = u''.join(result)
	if result.find(u' ') >= 0:
		test2 = ''.join(result.split(' '))
		result = result.replace(u'\u3002 ', u'\u3002')
		result = result.replace(u'\uff0c ', u'\uff0c')
		result = result.replace(u'\uff1a ', u'\uff1a')
		#assert result == test2
		if result != test2:
			print >> sys.stderr, 'Error: unexpected space'
			print >> sys.stderr, result.replace('\n', '\\n').encode('gbk', 'replace')
			print >> sys.stderr, test2.replace('\n', '\\n').encode('gbk', 'replace')
	#print synonyms
	#print result.encode('gbk', 'replace')
	return synonyms, result

filelist = glob.glob(whatfile)
filenum = len(filelist)
num = 0
errorfiles = []
result = []
fp = open(outfile, 'w')
fp.close()
for filename in filelist:
	num += 1
	print >> sys.stderr, filename, num, 'of', filenum
	try:
		fp = open(filename, 'r')
		s = fp.read()
		s = '[['.join(map(string.strip, s.split('<<')))
		s = ']]'.join(map(string.strip, s.split('>>')))
		doc = libxml2dom.parseString(s, html=1, 
				htmlencoding='utf-8')
		fp.close()
		titles = doc.getElementsByTagName("h1")
		title = titles[0].textContent
		assert title.find('|') < 0
		#print title.encode('gbk', 'replace')
		divs = doc.getElementsByTagName("div")
		found = False
		for div in divs:
			if div.getAttribute('class') != 'article' or\
				not div.getAttribute('style').startswith('z-i'):
				continue
			#print div.textContent.encode('gbk', 'replace')
			#print div.toString(prettyprint=1)
			assert not found
			found = True
			sym, res = parseDiv(div)
			if sym and not title in sym:
				print >> sys.stderr, "Error: title not in sym"
				print >> sys.stderr, title.encode('gbk', 
						'replace'), sym
				sym = [title]
		result += [(sym or [title], res)]
		if len(result) == flushcnt:
			fp = open(outfile, 'a')
			for sym, res in result:
				print >> fp, u'|'.join(sym).encode('utf-8')
				print >> fp, afterword
				print >> fp, res.encode('utf-8')
				print >> fp, afteritem
			fp.close()
			result = []
	except:
		print >> sys.stderr, 'error occured'
		errorfiles += [filename]
		raise
		continue
if errorfiles:
	print >> sys.stderr, 'Error files:', '\n'.join(errorfiles)
fp = open(outfile, 'a')
for sym, res in result:
	print >> fp, u'|'.join(sym).encode('utf-8')
	print >> fp, afterword
	print >> fp, res.encode('utf-8')
	print >> fp, afteritem
fp.close()

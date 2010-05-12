#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, string, re

def firstmatch(ar, f, start=0, end=0):
	i = start
	if end == 0:
		end = len(ar)
	while i < end:
		if (f is None and ar[i]) or f(ar[i]):
			break
		i += 1
	if i >= end:
		i = -1
	return i

def recorddictitem(word, mean):
	print '%s\t%s' % (word, mean.replace('\\n','\\\\n').replace('\n','\\n'))

infwbracket = re.compile(r'［(.*?)］')
inbracket = re.compile(r'\[(.*?)\]')
xmltag = re.compile(r'<.*?>')
oneitem = re.compile(r"<a href='(.*?)'>(.*?)</a>")
hasfontsize2 = lambda s:s.find("<font size='+2'>") >= 0
hasfontsize1 = lambda s:s.find("<font size='+1'>") >= 0

_supsubmap = {
		'p': {
			'0': '⁰',
			'1': '¹',
			'2': '²',
			'3': '³',
			'4': '⁴',
			'5': '⁵',
			'6': '⁶',
			'7': '⁷',
			'8': '⁸',
			'9': '⁹',
			'+': '⁺',
			'-': '⁻',
			'=': '⁼',
			'(': '⁽',
			')': '⁾',
			'n': 'ⁿ',
			'i': 'ⁱ',
			u'･': '˙',
			'r': '^r',
			},
		'b': {
			'0': '₀',
			'1': '₁',
			'2': '₂',
			'3': '₃',
			'4': '₄',
			'5': '₅',
			'6': '₆',
			'7': '₇',
			'8': '₈',
			'9': '₉',
			'+': '₊',
			'-': '₋',
			'=': '₌',
			'(': '₍',
			')': '₎',
			'e': 'ₑ',
			},
		}

def replacesupsub(str, supsubmap=_supsubmap):
	ar = str.split('<su')
	result = [ar[0]]
	for s in ar[1:]:
		if not s or s[0] not in 'pb':
			result.append(s)
			continue
		assert s[1] == '>'
		p = s.index('</su' + s[:2])
		d = supsubmap[s[0]]
		for c in xmltag.sub('', s[2:p]).decode('utf-8'):
			if 0xFF10<= ord(c) <=0xFF19:
				c = chr(ord(c) - 0xFF10 + 0x30)
			result.append(d[c])
		result.append(s[p+6:])
	return ''.join(result);

def kakomishori(section, lines, start, end):
	index = []
	for i in xrange(start, end):
		m = oneitem.search(lines[i])
		assert m
		fname = m.group(1)
		title = xmltag.sub('', m.group(2))
		try:
			title = inbracket.findall(title)[0]
		except:
			pass
		index.append(title)
		f = open(fname, 'r')
		flines = f.readlines()
		f.close()
		p = firstmatch(flines, hasfontsize2)
		try:
			assert p > 0
			assert flines[-1].startswith('</div>')
		except:
			print >> sys.stderr, fname, title
			raise
		try:
			recorddictitem(title, section +
				xmltag.sub('', ''.join(map(replacesupsub,
					flines[p:-1]))))
		except:
			print >> sys.stderr, (u'%s: %s' % (section.decode('utf-8'), title.decode('utf-8'))).encode('gbk', 'replace')
			raise
		p = firstmatch(flines, hasfontsize1, p+1)
		while p > 0:
			paragraph = xmltag.sub('', flines[p]).strip()
			assert 0xFF10<=ord(paragraph.decode('utf-8')[0])<=0xFF19
			q = firstmatch(flines, hasfontsize1, p+1)
			for line in flines[p:q]:
				assert line.endswith('<br>\n')
				line = replacesupsub(line)
				line = xmltag.sub('', line).decode('utf-8')
				line = line.lstrip(u'　 \t')
				if line and line[0] in u'★¶☆':
					k = line.find(u'/')
					try:
						assert k > 0
					except:
						print >> sys.stderr, 'Warning: no slash:', (u'%s: %s: %s' % (section.decode('utf-8'), title.decode('utf-8'), line.rstrip())).encode('gbk', 'replace')
						continue
					recorddictitem(line[1:k].strip(u'　 \t'
						).encode('utf-8'), line[k+1:
							].encode('utf-8') +
						'%s%s - %s' % (section,
							title, paragraph))
			p = q
	try:
		section = infwbracket.findall(section)[0]
	except:
		pass
	recorddictitem(section, '\n'.join(index))

def doushishori(section, lines, start, end):
	index = []
	for i in xrange(start, end):
		m = oneitem.search(lines[i])
		assert m
		fname = m.group(1)
		title = xmltag.sub('', m.group(2))
		index.append(title)
		f = open(fname, 'r')
		flines = f.readlines()
		f.close()
		p = firstmatch(flines, hasfontsize2)
		try:
			assert p > 0
			assert flines[-1].startswith('</div>')
		except:
			print >> sys.stderr, fname, title
			raise
		recorddictitem('|'.join(inbracket.findall(title)[0].split(
			'　')), xmltag.sub('', ''.join(flines[p:-1])) + section)
	try:
		section = infwbracket.findall(section)[0]
	except:
		pass
	recorddictitem(section, '\n'.join(index))

def hokanoshori(section, lines, start, end):
	index = []
	for i in xrange(start, end):
		m = oneitem.search(lines[i])
		assert m
		fname = m.group(1)
		title = xmltag.sub('', m.group(2))
		f = open(fname, 'r')
		flines = f.readlines()
		f.close()
		p = firstmatch(flines, hasfontsize2)
		try:
			assert p > 0
			assert flines[-1].startswith('</div>')
		except:
			print >> sys.stderr, fname, title
			raise
		if flines[p].find('<span') < 0:
			index.append(title)
			recorddictitem(title, xmltag.sub(
				'', ''.join(flines[p+1:-1])) + section)
			for line in flines[p+1:-1]:
				if line.startswith('《'):
					assert line.endswith('行》<br>\n')
					continue
				elif line.startswith('国名・地域名') or line.\
						startswith('※') or line.\
						startswith('注：') or line.\
						startswith('州名（'):
					continue
				try:
					p = line.index('<span')
				except:
					print >> sys.stderr, fname, title
					print >> sys.stderr, line
					raise
				recorddictitem(line[:p].decode('utf-8').strip(
					u'　 \t/').encode('utf-8'), xmltag.sub(
						'', line[p:]) + '［%s - %s］'
					% (section, title))
		else:
			title = inbracket.findall(title)[0]
			index.append(title)
			recorddictitem(title, xmltag.sub(
				'', ''.join(flines[p:-1])) + section)
	try:
		section = infwbracket.findall(section)[0]
	except:
		pass
	recorddictitem(section, '\n'.join(index))


assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s idx??.html" % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'r')
lines = f.readlines()
f.close()

hastable = lambda s: s.find('<table>') >= 0
hasclosediv = lambda s: s.find('</div>') >= 0
anchorname = re.compile(r"<a name='(.*?)'>")
index = []
p = firstmatch(lines, hastable)
while p >= 0:
	assert lines[p].find('<div') >= 0
	section = anchorname.findall(lines[p])[0]
	q = firstmatch(lines, hasclosediv, p);
	if section == '［囲み］':
		kakomishori(section, lines, p+1, q)
	elif section == '［動作動詞コラム］':
		doushishori(section, lines, p+1, q)
	else:
		hokanoshori(section, lines, p+1, q)
	try:
		section = infwbracket.findall(section)[0]
	except:
		pass
	index.append(section);
	p = firstmatch(lines, hastable, q);
recorddictitem(' ', '\n'.join(index))

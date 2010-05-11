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

xmltag = re.compile(r'<.*?>')
oneitem = re.compile(r"<a href='(.*?)'>(.*?)</a>")
hasfontsize2 = lambda s:s.find("<font size='+2'>") >= 0
hasfontsize1 = lambda s:s.find("<font size='+1'>") >= 0

def kakomishori(section, lines, start, end):
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
		recorddictitem(title, section +
				xmltag.sub('', ''.join(flines[p:-1])))
		p = firstmatch(flines, hasfontsize1, p+1)
		while p > 0:
			paragraph = xmltag.sub('', flines[p]).strip()
			assert 0xFF10<=ord(paragraph.decode('utf-8')[0])<=0xFF19
			q = firstmatch(flines, hasfontsize1, p+1)
			for line in flines[p:q]:
				assert line.endswith('<br>\n')
				line = xmltag.sub('', line).decode('utf-8')
				line = line.lstrip(u'　 \t')
				if line and line[0] in u'★¶':
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

inbracket = re.compile(r'\[(.*?)\]')

def doushishori(section, lines, start, end):
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
		recorddictitem('|'.join(inbracket.findall(title)[0].split(
			'　')), xmltag.sub('', ''.join(flines[p:-1])) + section)

def hokanoshori(section, lines, start, end):
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
			recorddictitem(inbracket.findall(title)[0], xmltag.sub(
				'', ''.join(flines[p:-1])) + section)


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
	p = firstmatch(lines, hastable, q);

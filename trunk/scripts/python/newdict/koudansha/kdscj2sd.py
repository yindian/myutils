#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, re
import unicodedata
import pdb

def charref2ustr(str):
	ar = str.decode('sjis').split('&#');
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s[0] != 'x':
			result.append(unichr(int(s[:p])))
		else:
			result.append(unichr(int(s[1:p], 16)))
		result.append(s[p+1:])
	return u''.join(result)

def pinyin2ascii(str):
	str = unicodedata.normalize('NFD', str)
	return ''.join(filter(lambda c: c.isalpha(), str)).encode('ascii')

double = re.compile(r'【(.*?)】')
zhspan = re.compile(r'<SPAN lang=zh>(.*?)</SPAN>')
xmltag = re.compile(r'<.*?>')
enc = lambda s: s.encode('gb18030')

def gettitlepronun(line):
	title = map(charref2ustr, zhspan.findall(line))
	if not title:
		title = map(charref2ustr, double.findall(line))
	if line.find('<', 1) < 0:
		assert not title
		title  = [charref2ustr(line[line.find('>')+1:].strip())]
	assert title or line.find('〓') > 0
	title = [xmltag.sub('', s) for s in title]
	p = line.rfind('</SPAN>')
	q = -1
	if line.find('entryhilight') > 0:
		q = p
		p = line.rfind('</SPAN>', 0, p)
	if p > 0:
		pronun = charref2ustr(line[p + len('</SPAN>'):q])
		pronun = xmltag.sub('', pronun).strip()
		pronun = pinyin2ascii(pronun)
	else:
		pronun = ''
	return title, pronun

totalresult = []
totaltitle = []
def flushitem(item):
	title = '|'.join(item[0])
	# pronun is discarded
	str = charref2ustr(''.join(item[2:]))
	str = str.replace('.bmp"', '.png"')
	try:
		stack = []
		ar = str.split('<')
		for s in ar[1:]:
			p = s.index('>')
			t = s[:p].split()[0]
			if t.startswith('/'):
				assert stack[-1] == t[1:]
				del stack[-1]
			elif t not in ('br', 'IMG'):
				stack.append(t)
		assert not stack
	except:
		print >> sys.stderr, title.encode('gb18030')
		print >> sys.stderr, str.encode('gb18030')
		print >> sys.stderr, stack, s.encode('gb18030')
		raise
	if str.endswith('<br>'):
		str = str[:-4]
	totalresult.append('%s\t%s\n' % (title, str))
	totaltitle.append(item[0] and item[0][0] or '')

annexpat = re.compile(ur'([0-9A-Za-z.．（）-]*<SPAN lang=zh>.*</SPAN>)([^<>]*)')

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s dump.htm' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'r')
state = 0
item = None
for line in f:
	if state == 0:
		if line.startswith('<DL>'):
			state = 1
	elif state == 1:
		assert line.startswith('<DT')
		title, pronun = gettitlepronun(line)
		p = line.index('>')
		item = [title, pronun, line[p+1:].rstrip()+'<br>']
		state = 2
	elif state == 2:
		if line.startswith('<DT'):
			flushitem(item)
			title, pronun = gettitlepronun(line)
			p = line.index('>')
			item = [title, pronun, line[p+1:].rstrip()+'<br>']
		elif line.startswith('</DD>') or line.startswith('</DL>'):
			flushitem(item)
			break
		elif line.startswith('<DD'):
			p = line.index('>')
			s = line[4:p]
			p += 1
			if s.endswith('example'):
				item.append('　　¶%s<br>' % (
						line[p:].rstrip(),))
			else:
				item.append(line[p:].rstrip() + '<br>')
		elif line == '<DIV></DIV>\n':
			item.append('<br>')
		elif line.startswith('<DIV'):
			assert line.startswith('<DIV class=')
			p = line.find('>')
			s = line[11:p]
			ll = line.rstrip()
			lp = line[:p+1]
			t = line[p+1:].rstrip()
			if s in ('tangocho', 'ruigigo'):
				item.append(ll)
				continue
			try:
				if not t.endswith('</DIV>'):
					assert s == 'subbody'
					assert not t
					state = 3
					item.append(ll)
					continue
			except:
				print >> sys.stderr, line
				raise
			if s == 'subtitle':
				item.append('<b>%s</b><br>' % (ll,))
			elif s == 'subbody':
				item.append(ll + '<br>')
			elif s == 'example':
				item.append('%s　　¶%s<br>'% (lp, t,))
			else:
				print >> sys.stderr, 'Errrrrrr'
				pdb.set_trace()
	elif state == 3:
		s = line.rstrip()
		if s.endswith('</DIV></DIV>') or s.endswith('</TABLE></DIV>'):
			item.append('%s<br>' % (s,))
			state = 2
		else:
			item.append(s)
	else:
		print >> sys.stderr, 'Ooops'
		pdb.set_trace()
f.close()
result = ''.join(totalresult).encode('utf-8')
hrefpat = re.compile(r'<A href="#([^"]*)">')
result = hrefpat.sub(lambda m: '<A href="bword://%s">' % (totaltitle[int(
	m.group(1))].encode('utf-8'),), result)
spanpat = re.compile(r'</?SPAN[^>]*>')
result = spanpat.sub('', result)
sys.stdout.write(result)

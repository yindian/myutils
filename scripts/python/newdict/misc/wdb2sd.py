#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import glob
import re
import traceback

def charref2uni(str):
	ar = str.decode('utf-8').split('&');
	result = [ar[0]]
	for s in ar[1:]:
		try:
			p = s.index(';')
			q = p+1
		except:
			if s.startswith('#'):
				p = 1
				if s[p] == 'x':
					p += 1
					int(s[p:p+4], 16)
					p += 4
				else:
					while s[p].isdigit():
						p += 1
				q = p
			else:
				print >> sys.stderr, str
				print >> sys.stderr, ar
				raise Exception('Unexpected ' + s)
		if s.startswith('#x'):
			code = int(s[2:p], 16)
		elif s.startswith('#'):
			code = int(s[1:p])
		else:
			raise Exception('Unexpected #' + s[:p])
		if not 0x80 <= code < 0xA0:
			result.append(unichr(code))
		else:
			print >> sys.stderr, 'ignore', code, 'in', s
		result.append(s[q:])
	return u''.join(result).encode('utf-8')

def charrefstripcontrol(str):
	ar = str.split('&');
	result = [ar[0]]
	for s in ar[1:]:
		try:
			p = s.index(';')
			q = p+1
		except:
			if s.startswith('#'):
				p = 1
				if s[p] == 'x':
					p += 1
					int(s[p:p+4], 16)
					p += 4
				else:
					while s[p].isdigit():
						p += 1
				q = p
			else:
				p = q = 0
		if s.startswith('#x'):
			code = int(s[2:p], 16)
		elif s.startswith('#'):
			code = int(s[1:p])
		else:
			code = -1
		if 0x80 <= code < 0xA0:
			result.append(s[q:])
		elif code == 0xA0:
			result.append('&nbsp;')
			result.append(s[q:])
		elif code == 60:
			result.append('&lt;')
			result.append(s[q:])
		elif code == 62:
			result.append('&gt;')
			result.append(s[q:])
		else:
			result.append('&')
			result.append(s)
	return ''.join(result)

recognized_fixed_tag = set('''\
b>
/b>
big>
/big>
i>
/i>
s>
/s>
sub>
/sub>
sup>
/sup>
small>
/small>
tt>
/tt>
u>
/u>
br>
nl>
hr>
/font>
/a>'''.splitlines())

no_matching_tags = set(['br', 'nl', 'hr'])
def adjustimgstack(s):
	ar = s.split('<')
	result = [ar[0]]
	stack = []
	for s in ar[1:]:
		try:
			try:
				p = s.index('>')
			except:
				result.append('<')
				result.append(s)
				continue
			tag = s[:p].lower()
			if tag + '>' in recognized_fixed_tag:
				if tag not in no_matching_tags:
					if tag[0] == '/':
						tag = tag[1:]
						try:
							assert stack[-1] == tag
							del stack[-1]
						except:
							while stack and stack[-1] != tag:
								del stack[-1]
							if stack and stack[-1] == tag:
								del stack[-1]
					else:
						stack.append(tag)
			elif tag.startswith('font'):
				stack.append('font')
			elif tag.startswith('a '):
				stack.append('a')
			if tag.startswith('img'):
				for t in stack[::-1]:
					result.append('</%s>' % (t,))
				result.append('<')
				result.append(s[:p+1].replace('contents/common-content/wbe-content/di/gf/tx/', ''))
				for t in stack:
					result.append('<%s>' % (t,))
				result.append(s[p+1:])
			else:
				result.append('<')
				result.append(s)
		except:
			print >> sys.stderr, stack
			print >> sys.stderr, tag, s
			print >> sys.stderr, ''.join(result)
			raise
	return ''.join(result)

headwordpat = re.compile(r'<span class="wb-dict-headword">(.*?)</span>')
bpat = re.compile(r'</?B>(.*?)</?B>')
ahrefjspat = re.compile(r'''<a href="javascript:showEntry\('([^']*)', '[^']*'\)" target="_top">''')
tagpat = re.compile(r'<[^>]*>')

assert __name__ == '__main__'

flist = glob.glob('*/di*')
flist.sort()
for fname in flist:
	f = open(fname)
	buf = f.read()
	f.close()
	try:
		try:
			p = buf.index('<FONT class="dictionary">')
		except:
			if 0 < buf.find('The requested resource') < buf.find('is not available'):
				#missing
				continue
		p = buf.index('\n', p) + 1
		q = buf.index('\n</FONT>\n', p)
		buf = buf[p:q].strip()
		if not buf:
			#empty
			continue
		buf = charrefstripcontrol(buf)
		words = headwordpat.findall(buf)
		words = [words[0]] + sorted(list(set(words).difference(set([words[0]]))))
		if '<B>a</B>' in words and len(''.join(bpat.findall(charref2uni(words[0])))) > 1:
			s = set(words).difference(set([words[0]]))
			c = 'a'
			while '<B>%s</B>' % (c,) in s:
				s.remove('<B>%s</B>' % (c,))
				c = chr(ord(c) + 1)
			words = [words[0]] + sorted(list(s))
		words = [''.join(bpat.findall(charref2uni(s))) for s in words]
		mean = ahrefjspat.sub(r'<a href="bword://\g<1>">', buf.replace('<br/>', '<br>'))
		mean = adjustimgstack(mean)
		print '%s\t%s' % ('|'.join(words), mean.replace('\n', '\\n'))
	except:
		print >> sys.stderr, 'Error parsing', fname
		#traceback.print_exc()
		#continue
		raise

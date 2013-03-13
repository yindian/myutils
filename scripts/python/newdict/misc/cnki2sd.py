#!/usr/bin/env python
import sys, os.path
import re
import glob
import operator
from htmlentitydefs import name2codepoint

def charref2uni(str, x=True):
	ar = str.decode('utf-8').split('&');
	result = [ar[0]]
	for s in ar[1:]:
		try:
			p = s.index(';')
			r = s[p+1:]
		except:
			p = 0
			if s[p] == '#':
				p += 1
				if s[p].lower() == 'x':
					p += 1
					while p < len(s) and s[p] in string.hexdigits:
						p += 1
				else:
					while p < len(s) and s[p].isdigit():
						p += 1
			else:
				while p < len(s) and s[p].isalpha():
					p += 1
			r = s[p:]
			if not p:
				raise
		if s.startswith(' '):
			t = s[:p].replace(' ', '')
		else:
			t = s[:p]
		try:
			if t.startswith('#x'):
				assert x
				result.append(unichr(int(t[2:], 16),))
			elif t.startswith('#'):
				result.append(unichr(int(t[1:]),))
			else:
				assert x
				result.append(unichr(name2codepoint[t],))
		except Exception, e:
			if not isinstance(e, AssertionError):
				print >> sys.stderr, 'Ignore Error: invalid entity', t.encode('utf-8')
			result.append('&')
			result.append(t)
			result.append(';')
		result.append(r)
	return u''.join(result).encode('utf-8')


assert __name__ == '__main__'

if len(sys.argv) < 2:
	print 'Usage: %s filename_pattern' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

flist = reduce(operator.add, map(glob.glob, sys.argv[1:]))
recidpat = re.compile(r'recid=([^&]*)', re.I)
ar = [(recidpat.findall(s)[0].lower(), s) for s in flist]
ar.sort()
flist = [t[1] for t in ar]
del ar

tagpat = re.compile(r'<[^>]*>')
imgpat = re.compile(r'<img[^>]*src="([^"]*)"[^>]*>')
rmprefix = lambda s: s.startswith(',') and s[s.index('+')+1:] or s
imgsub = lambda m: '<img src="%s">' % (rmprefix(os.path.basename(m.group(1))),)
imgpathpat = re.compile(r'<table[^>]*imgpath="([^"]*)"[^>]*>')
imgpathsub = lambda m: '<img src="%s">%s' % (os.path.basename(m.group(1)), m.group(0))
surrogatepat = re.compile(r'&#(5[56]\d{3});&#(5[67]\d{3});')
surrogatesub = lambda m: (unichr(int(m.group(1))) + unichr(int(m.group(2)))).encode('utf-8')
charrefpat = re.compile(r'&#(\d*);')
charrefsub = lambda m: unichr(int(m.group(1))).encode('utf-8')
pinyinpat = re.compile(u'[ /a-z\u0101\u00E1\u01CE\u00E0\u014D\u00F3\u01D2\u00F2\u0113\u00E9\u011B\u00E8\u012B\u00ED\u01D0\u00EC\u016B\u00FA\u01D4\u00F9\u00FC\u01D6\u01D8\u01DA\u01DC\u00EA\u1EBF\u1EC1\uE7C7\u0144\u0148\uE7C8\u0251\u0261\u012D\u0103\u0115\u016D\u014F\u1E3F\u01F9]+', re.I)

def meanimgdo(mean):
	if mean[-1].find('<img') >= 0:
		ar = imgpat.findall(mean[-1])
		for s in ar:
			print >> sys.stderr, s[s.index('/CRFDPIC'):]
		mean[-1] = imgpat.sub(imgsub, mean[-1])
	if mean[-1].find('imgpath') >= 0:
		ar = imgpathpat.findall(mean[-1])
		for s in ar:
			print >> sys.stderr, s[s.index('/CRFDPIC'):]
		mean[-1] = imgpathpat.sub(imgpathsub, mean[-1])

for fname in flist:
	f = open(fname)
	word = []
	mean = []
	state = 0
	lineno = 0
	lastline = None
	try:
		for line in f:
			lineno += 1
			if state == 0:
				if line.lstrip().startswith('<!-- content title -->'):
					state = 1
			elif state == 1:
				if line.lstrip().startswith('<!-- content text -->'):
					if mean:
						mean = ['<b>%s</b><br>' % (' '.join(mean),)]
						meanimgdo(mean)
					elif tagpat.findall(word[0]):
						mean = ['<b>%s</b><br>' % (word[0],)]
						meanimgdo(mean)
					state = 2
				elif lastline:
					line = lastline.rstrip() + line
					p = line.index('<span id="title')
					p = line.index('>', p + 15) + 1
					q = line.rindex('</span>')
					lastline = None
					if q > p:
						word.append(line[p:q])
						assert word[-1].find('|') < 0
						if len(word) > 1 and not mean:
							mean.extend(word)
						elif mean:
							mean.append(word[-1])
						if line[p-11:p-2] == 'OtherText':
							del word[-1]
						elif line[p-4:p-2] == 'PY':
							ar = [s.strip().encode('utf-8') for s in pinyinpat.findall(word[-1].decode('utf-8'))]
							del word[-1]
							word.extend(ar)
				else:
					p = line.find('<span id="title')
					if p >= 0:
						p = line.index('>', p + 15) + 1
						try:
							q = line.rindex('</span>')
						except:
							lastline = line
							continue
						else:
							lastline = None
						if q > p:
							word.append(line[p:q])
							assert word[-1].find('|') < 0
							if len(word) > 1 and not mean:
								mean.extend(word)
							elif mean:
								mean.append(word[-1])
							if line[p-11:p-2] == 'OtherText':
								del word[-1]
							elif line[p-4:p-2] == 'PY':
								ar = [s.strip().encode('utf-8') for s in pinyinpat.findall(word[-1].decode('utf-8'))]
								del word[-1]
								word.extend(ar)
			elif state == 2:
				if line.lstrip().startswith('<!-- other start -->'):
					state = 3
				elif line.startswith('                <div class="contentText" id="lblContent">'):
					pass
				elif line.startswith('                </div>'):
					pass
				else:
					if line[:20].isspace():
						mean.append(line[20:].rstrip())
					else:
						mean.append(line.strip())
					meanimgdo(mean)
			else:
				break
	except:
		print >> sys.stderr, 'Error processing line', lineno, 'in', fname
		raise
	f.close()
	try:
		print '%s\t%s' % (charref2uni('|'.join(map(lambda s: tagpat.sub('', s), word))), charref2uni('\\n'.join(mean), False))
	except:
		print >> sys.stderr, 'Error processing', fname
		raise

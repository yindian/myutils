#!/usr/bin/env python
import sys, os.path
import re
import glob
import operator
from htmlentitydefs import name2codepoint

def charref2uni(str):
	ar = str.split('&');
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s.startswith('#x'):
			result.append('%04X' % (int(s[2:p], 16),))
		elif s.startswith('#'):
			result.append('%04X' % (int(s[1:p]),))
		else:
			result.append('%04X' % (name2codepoint[s[:p]],))
		result.append(s[p+1:])
	return ''.join(result)


assert __name__ == '__main__'

if len(sys.argv) < 2:
	print 'Usage: %s filename_pattern' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

flist = reduce(operator.add, map(glob.glob, sys.argv[1:]))
ar = [(s[s.index('=')+1:], s) for s in flist]
ar.sort()
flist = [t[1] for t in ar]
del ar

imgpat = re.compile(r'<img[^>]*src="([^"]*)"[^>]*>')
imgsub = lambda m: '<img src="%s">' % (os.path.basename(m.group(1)),)
imgpathpat = re.compile(r'<table[^>]*imgpath="([^"]*)"[^>]*>')
imgpathsub = lambda m: '<img src="%s">%s' % (os.path.basename(m.group(1)), m.group(0))

for fname in flist:
	f = open(fname)
	word = []
	mean = []
	state = 0
	lineno = 0
	for line in f:
		lineno += 1
		try:
			if state == 0:
				if line.lstrip().startswith('<!-- content title -->'):
					state = 1
			elif state == 1:
				if line.lstrip().startswith('<!-- content text -->'):
					if mean:
						mean = ['<b>%s</b><br>' % (' '.join(mean),)]
					state = 2
				else:
					p = line.find('<span id="title')
					if p >= 0:
						p = line.index('>', p + 15) + 1
						q = line.index('<', p)
						if q > p:
							word.append(line[p:q])
							assert word[-1].find('|') < 0
							if len(word) > 1 and not mean:
								mean.extend(word)
							elif mean:
								mean.append(word[-1])
							if line[p-11:p-2] == 'OtherText':
								del word[-1]
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
			else:
				break
		except:
			print >> sys.stderr, 'Error processing line', lineno, 'in', fname
			raise
	f.close()
	print '%s\t%s' % (charref2uni('|'.join(word)), '\\n'.join(mean))

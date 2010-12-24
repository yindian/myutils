# -*- coding: utf-8 -*-
import sys, re
f = open(sys.argv[1], 'r')
htmlquote = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace(
		'>', '&gt;').replace('"', '&quot;')
htmlunquote = lambda s: s.replace('&lt;', '<').replace('&gt;', '>').replace(
		'&quot;', '"').replace('&amp;', '&')
respat = re.compile(r'(?<!&lt;nowiki&gt;)\[\[(?:File|Image|图像|圖像|文件|檔案|档案):\s*([^\]\|<>]*?)\s*((?:\|[^\]]*)?)\]\]', re.I)
resrepl = lambda m: '[[<rref>%s</rref>%s]]' % (htmlunquote(m.group(1)), 
		m.group(2))
stripprefix = lambda s: s.find(':') >= 0 and s[s.find(':')+1:].strip() or s.strip()
reslist = []
lineno = 0
try:
	for line in f:
		lineno += 1
		word, mean = line.rstrip('\r\n').split('\t', 1)
		ar = htmlquote(mean.replace('‎', '')).split('\\n')
		state = 0
		for i in xrange(len(ar)):
			if state == 0:
				if ar[i].find('&lt;gallery&gt;') >= 0:
					state = 1
				else:
					reslist.extend([htmlunquote(a[0])
						for a in
						respat.findall(ar[i])])
					ar[i] = respat.sub(resrepl, ar[i])
			if state == 1:
				if ar[i].find('&lt;/gallery&gt;') >= 0:
					state = 0
				elif ar[i].find('&lt;gallery&gt;') >= 0:
					pass
				elif ar[i].strip():
					p = ar[i].find('|')
					if p < 0:
						p = len(ar[i])
					reslist.append(htmlunquote(
						stripprefix(ar[i][:p])))
					ar[i] = '%s|%s' % (htmlunquote(
						stripprefix(ar[i][:p])),
						ar[i][p+1:])
		mean = ''.join(ar)
		print '%s\t%s' % (word, mean)
except:
	print >> sys.stderr, 'Error on line', lineno
	raise
f.close()
resset = set()
for s in reslist:
	if s not in resset:
		print >> sys.stderr, s
		resset.add(s)

# -*- coding: utf-8 -*-
import sys, re
f = open(sys.argv[1], 'r')
htmlquote = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace(
		'>', '&gt;').replace('"', '&quot;')
respat = re.compile(r'\[\[(?:File|Image|图像|圖像|文件|檔案):\s*([^\]\|<>]*?)\s*((?:\|[^\]]*)?)\]\]', re.I)
stripprefix = lambda s: s.find(':') >= 0 and s[s.find(':')+1].strip() or s.strip()
reslist = []
lineno = 0
try:
	for line in f:
		lineno += 1
		word, mean = line.rstrip('\r\n').split('\t', 1)
		ar = mean.replace('‎', '').split('\n')
		state = 0
		for i in xrange(len(ar)):
			if state == 0:
				if ar[i].find('&lt;gallery&gt;') >= 0:
					state = 1
				else:
					reslist.extend([a[0] for a in
						respat.findall(ar[i])])
					ar[i] = respat.sub('[[<rref>\g<1>'
							'</rref>\g<2>]]' ,
							ar[i])
			else:
				if ar[i].find('&lt;/gallery&gt;') >= 0:
					state = 0
				else:
					p = ar[i].index('|')
					reslist.append(stripprefix(ar[i][:p]))
					ar[i] = '%s|%s' % (stripprefix(
						ar[i][:p]),
						ar[i][p+1:])
		mean = htmlquote(''.join(ar))
		mean = mean.replace('&lt;rref&gt;', '<rref>').replace(
				    '&lt;/rref&gt;', '</rref>')
		print '%s\t%s' % (word, mean)
except:
	print >> sys.stderr, 'Error on line', lineno
	raise
f.close()
resset = set(reslist)
for s in sorted(resset):
	print >> sys.stderr, s

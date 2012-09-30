import sys, re
bpat = re.compile(r'<b>([^<>]*?)</b>')
htmlunquote = lambda s: s.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')
def stripparen(s):
	p = s.find('(')
	q = s.find(')')
	if p == 0:
		if q == len(s)-1:
			return s[p+1:q]
		else:
			return s[q+1:].strip()
	else:
		return s
f = open(sys.argv[1], 'r')
lineno = 0
try:
	for line in f:
		lineno += 1
		word, mean = line.rstrip('\n').split('\t', 1)
		try:
			ar = word.split(', ')
			p = -1
			for i in xrange(len(ar)):
				if ar[i].startswith('and '):
					p = i+1
					break
			if p > 0:
				for i in xrange(p, len(ar)):
					assert not ar[i].startswith('and ')
				alt = [' '.join(ar[p:][::-1]) + ' ' + ', '.join(ar[:p])]
			else:
				alt = [' '.join(ar[::-1])]
			ar = mean.split('\\n')
			for s in ar[:5]:
				s = s.strip()
				if s.startswith('<i>'):
					br = bpat.findall(s)
					for t in br:
						if not t.islower():
							alt.append(stripparen(
								htmlunquote(
								t).strip(' ,')))
		except:
			print >> sys.stderr, 'Line', lineno
			alt = None
		if alt:
			ar = [word]
			for s in alt:
				if s not in ar:
					ar.append(s)
			print '%s\t%s' % ('|'.join(ar), mean)
			if len(ar) > 1:
				print >> sys.stderr, lineno, '|'.join(ar)
		else:
			print '%s\t%s' % (word, mean)
except:
	print >> sys.stderr, 'Line', lineno
	raise
f.close()

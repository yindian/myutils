import sys, string, re
nonasciichar = re.compile(ur'[^\x00-\x7f\u00B7\u3000]')

f = open(sys.argv[1], 'r')
phonlines = f.readlines()
f.close()
f = open(sys.argv[2], 'r')
gianlines = f.readlines()
f.close()

unquote = lambda s: s.replace('&quot;', '"').replace('&apos;', "'")

assert len(phonlines) == len(gianlines)
for i in xrange(len(phonlines)):
	try:
		phonword, phonmean = phonlines[i].split('\t', 1)
		gianword, gianmean = gianlines[i].split('\t', 1)
		gianword = map(string.strip, gianword.split('|'))
		assert unquote(phonword) == gianword[0]
		phonmean = phonmean.decode('utf-8')
		gianmean = gianmean.decode('utf-8')
		sa = nonasciichar.findall(phonmean)
		sb = nonasciichar.findall(gianmean)
		assert len(sa) == len(sb)
		ta = nonasciichar.split(phonmean)
		assert len(ta) == len(sa) + 1
		result = [ta[0]]
		for i in xrange(len(sa)):
			result.append(sb[i])
			result.append(ta[i+1])
		gianmean = u''.join(result).encode('utf-8')
		sys.stdout.write('%s\t%s' % ('|'.join(gianword), gianmean))
	except AssertionError:
		print >> sys.stderr, 'Line %d, sa(%d) sb(%d)' % (i+1,
				len(sa), len(sb))
		print >> sys.stderr, u''.join(sa).encode('gb18030')
		print >> sys.stderr, u''.join(sb).encode('gb18030')
		raise

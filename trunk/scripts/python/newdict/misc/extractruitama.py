#!/usr/bin/env python
import sys, os.path, re
import traceback

recode = lambda s: s.decode('utf-8').encode('gb18030')

def findline(lines, s, start=0, rise=False):
	for i in xrange(start, len(lines)):
		if lines[i].startswith(s):
			return i
	if rise:
		raise IndexError('Cannot find %s in lines%s' % (s, start and
			'[%d:]' % (start,) or ''))
	return -1

def findlinecontain(lines, s, start=0, rise=False):
	for i in xrange(start, len(lines)):
		if lines[i].find(s) >= 0:
			return i
	if rise:
		raise IndexError('Cannot find %s in lines%s' % (s, start and
			'[%d:]' % (start,) or ''))
	return -1

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s data_index_num.htm' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

wordlist = []
indexlist = [sys.argv[1]]
taglist = []

lipat = re.compile(r'<li>(\d+)\s*<a href="(.*?)">(.*?)</a></li>')
hrefurlpat = re.compile(r'<a href="(.*?)">')
while indexlist:
	fname = indexlist.pop(0)
	f = open(fname, 'r')
	lines = f.readlines()
	f.close()
	p = findline(lines, '<ul>') + 1
	q = findline(lines, '</ul>', p)
	r = findline(lines, '<a href', q)
	try:
		assert 0 < p < q < r
	except:
		#print >> sys.stderr, 'Error processing', fname, p, q, r
		pass
	for i in xrange(p, q > 0 and q or len(lines) + q):
		m = lipat.match(lines[i])
		try:
			assert m
		except:
			if q < 0 and r < 0:
				break
			raise
		num, url, word = map(m.group, [1, 2, 3])
		url, tag = url.split('#')
		# special cases
		if url == '../data/e38292/e38292e381a8.html':
			url = '../data/e38292/e38292e3809c.html'
			tag = 'e38292e3809ce381a8e38197e3819f'
		wordlist.append((int(num), word, url, tag))
		taglist.append((tag, word))
	if r > 0:
		indexlist.append(hrefurlpat.findall(lines[r])[0])
taglist = dict(taglist)

#print len(wordlist)
#last = None
#for i in xrange(len(wordlist)):
#	num = wordlist[i][0]
#	if last and last+1 != num:
#		print 'Missing', last+1
#	if num != i+1:
#		print 'Wrong position:', num, i+1
#	last = num

lastfname = None
lastlines = None
dic = []
diclinkpat = re.compile(r" ?<a id='dictlink'.*?>(.*?)</a>")
hrefdatpat = re.compile(r'<a href="../../data/.*?#(.*?)">(.*?)</a>')
for num, word, fname, tag in wordlist:
	try:
		if fname == lastfname:
			lines = lastlines
		else:
			f = open(fname, 'r')
			lastfname = fname
			lastlines = lines = f.readlines()
			f.close()
		p = findlinecontain(lines, '<a name="%s">' % (tag,), rise=True)
		assert lines[p+1].startswith('<h2>')
		s = lines[p+1]
		result = [s[4:s.index('&nbsp;&nbsp; <a')].strip()]
		p = findline(lines, '<div id="outputarea">', p+2, rise=True)
		q = findline(lines, '</div>', p, rise=True)
		s = '\n'.join(lines[p:q])[21:]
		s = diclinkpat.sub('', s)
		result.append(s.strip())
	except:
		print >> sys.stderr, num, recode(word), fname
		dic.append((word, None))
		traceback.print_exc()
	else:
		dic.append((word, result))

hrefdatsub = lambda m: r'<a href="bword://%s">%s</a>' % (taglist.get(m.group(1),
	m.group(2)), m.group(2))
for word, mean in dic:
	mean = '<br>'.join(mean or [])
       	mean = hrefdatpat.sub(hrefdatsub, mean)
	print '%s\t%s' % (word, mean.replace('\n', '\\n'))

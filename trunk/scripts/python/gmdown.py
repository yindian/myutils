#!/usr/bin/env python
import sys, os, urllib, urllib2

def fnquote(s):
	return s.replace('/', '_').replace('\\', '_').replace(':', '_')

assert __name__ == '__main__'

maxnum = len(sys.argv) - 1
digits = maxnum > 99 and 3 or (maxnum > 9 and 2 or 1)
fnfmt = '%%0%dd. %%s.mp3' % (digits,)
idx = 0
for sid in sys.argv[1:]:
	idx += 1
	f = urllib2.urlopen('http://www.google.cn/music/top100/musicdownload?id=' + sid)
	buf = f.read()
	f.close()
	front = buf.index('<a href="/music/top100/url?q=http://') + 9
	last = buf.index('"><img src="', front)
	url = 'http://www.google.cn' + buf[front:last].replace('%3A', ':'
	).replace('%2F', '/').replace('&amp;', '&')
	front = buf.index('<tr class="meta-data-tr"><td class="td-song-name">') + 50
	last =buf.index('</td>', front)
	title = buf[front:last]
	print 'Downloading', fnfmt % (idx, title)
	f = urllib2.urlopen(url)
	g = open(fnquote(fnfmt % (idx, title)), 'wb')
	g.write(f.read())
	f.close()
	g.close()

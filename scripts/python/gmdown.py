#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, urllib, urllib2
import re, time, glob, traceback

pathspecial = re.compile(r'[/\\;:<>\?\*&|]')
pathspecial = re.compile(r'[/\\:]')
def fnquote(s):
	return pathspecial.sub('_', s)

assert __name__ == '__main__'

maxnum = len(sys.argv) - 1
digits = maxnum > 99 and 3 or (maxnum > 9 and 2 or 1)
fnfmt = '%%0%dd. %%s.mp3' % (digits,)
idx = 0
failids = []
site = 'aHR0cDovL3d3dy5nb29nbGUuY24='.decode('base64')
prefix = 'aHR0cDovL3d3dy5nb29nbGUuY24vbXVzaWMvdG9wMTAwL211c2ljZG93bmxvYWQ/aWQ9'.decode('base64')
for sid in sys.argv[1:]:
	idx += 1
	if glob.glob(fnfmt % (idx, '*')):
		print 'Skipping index', idx
		continue
	f = urllib2.urlopen(prefix + sid, timeout=30)
	buf = f.read()
	f.close()
	try:
		front = buf.index('<a href="/music/top100/url?q=http://') + 9
		last = buf.index('"><img src="', front)
		url = site + buf[front:last].replace('%3A', ':'
		).replace('%2F', '/').replace('&amp;', '&')
		front = buf.index('<tr class="meta-data-tr"><td class="td-song-name">') + 50
		last =buf.index('</td>', front)
		title = buf[front:last]
	except:
		try:
			assert buf.find('captcha') > 0
			while True:
				try:
					front = buf.index('<div class="captchaImage"><img src="') + 36
					end = buf.index('"', front)
					url = site + buf[front:end]
					captcha = raw_input('Please input captcha text for ' + url + ' : ')
					front = buf.index('<input type="hidden" name="tok" value="', front) + 39
					end = buf.index('"', front)
					tok = buf[front:end]
					f = urllib2.urlopen(prefix + sid + '&tok=' + tok + '&response=' + captcha + '&submitBtn=' + urllib.quote('提交'), timeout=30)
					buf = f.read()
					f.close()
					front = buf.index('<a href="/music/top100/url?q=http://') + 9
					last = buf.index('"><img src="', front)
					url = site + buf[front:last].replace('%3A', ':'
					).replace('%2F', '/').replace('&amp;', '&')
					front = buf.index('<tr class="meta-data-tr"><td class="td-song-name">') + 50
					last =buf.index('</td>', front)
					title = buf[front:last]
				except ValueError:
					continue
				else:
					break
		except:
			traceback.print_exc()
			f = open('musicdownload' + sid, 'w')
			f.write(buf)
			f.close()
			failids.append(sid)
			print >> sys.stderr, 'Failed for', sid
			time.sleep(5)
			continue
	fname = fnquote(fnfmt % (idx, title))
	if not os.path.exists(fname):
		print 'Downloading', fname
		f = urllib2.urlopen(url, timeout=30)
		g = open(fname, 'wb')
		g.write(f.read())
		f.close()
		g.close()
	else:
		print 'Skipping', fname
		time.sleep(2)
f = open('fail.txt', 'w')
f.write('\n'.join(failids))
f.close()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re, urllib, urllib2

def win32_utf8_argv():
	try:
		from ctypes import POINTER, byref, cdll, c_int, windll
		from ctypes.wintypes import LPCWSTR, LPWSTR

		GetCommandLineW = cdll.kernel32.GetCommandLineW
		GetCommandLineW.argtypes = []
		GetCommandLineW.restype = LPCWSTR

		CommandLineToArgvW = windll.shell32.CommandLineToArgvW
		CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
		CommandLineToArgvW.restype = POINTER(LPWSTR)

		cmd = GetCommandLineW()
		argc = c_int(0)
		argv = CommandLineToArgvW(cmd, byref(argc))
		if argc.value > 0:
			# Remove Python executable if present
			start = argc.value - len(sys.argv)
			return [argv[i].encode('utf-8') for i in
					xrange(start, argc.value)]
	except Exception:
		pass

fnenc = sys.getfilesystemencoding()

try:
	from ctypes import windll
	from ctypes.wintypes import DWORD
	STD_OUTPUT_HANDLE = DWORD(-11)
	STD_ERROR_HANDLE = DWORD(-12)
	GetStdHandle = windll.kernel32.GetStdHandle
	WriteConsoleW = windll.kernel32.WriteConsoleW

	def writeunicode(ustr, file=sys.stdout, newline=True):
		if file in (sys.stdout, sys.stderr) and file.isatty():
			which = file==sys.stdout and STD_OUTPUT_HANDLE or STD_ERROR_HANDLE;
			handle = GetStdHandle(which)
			if not isinstance(ustr, unicode):
				ustr = unicode(ustr)
			WriteConsoleW(handle, ustr, len(ustr), None, 0)
			if newline:
				print >> file
		else:
			if newline:
				print >> file, ustr.encode(fnenc, 'replace')
			else:
				file.write(ustr.encode(fnenc, 'replace'))
except:
	def writeunicode(ustr, file=sys.stdout, newline=True):
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

DOMAIN = 'YmFpZHUuY29t'.decode('base64')
SPACE = 'aGk='.decode('base64')
PHOTO = 'aGlwaG90b3M='.decode('base64')

divpagepat = re.compile(r'<div id="page">(.*?)</div>', re.S)
def samepage(a, b):
	return a and b and divpagepat.findall(a) == divpagepat.findall(b)

pathspecial = re.compile(r'[/\\;:<>\?\*&]')
def pathquote(s):
	return pathspecial.sub('_', s)

def getalbumlistbyuser(user):
	quser = urllib.quote(user)
	urlpat = 'http://%s.%s/%s/album/index/%%d' % (SPACE, DOMAIN,
			quser.replace('%', '%%'))
	albpat = re.compile(r'imgarr\[len\]={purl:"/%s/album/(.+?)"' % (quser,))
	numpat = re.compile(r'pnum:"(.+?)",')
	lastpage = None
	result = []
	numresult = []
	for i in xrange(sys.maxint):
		r = urllib2.urlopen(urlpat % (i,))
		page = r.read()
		if samepage(page, lastpage):
			break
		result.extend(albpat.findall(page))
		numresult.extend(numpat.findall(page))
		lastpage = page
	assert len(result) == len(numresult)
	return zip([urllib.unquote(s) for s in result], map(int, numresult))

def downloadalbum(user, album, namingrule='%d_%s.jpg', outpath='.', log=None,
		touni=lambda s: s.decode('cp936'), test=False):
	quser = urllib.quote(user)
	qalbum = urllib.quote(album)
	urlpat = 'http://%s.%s/%s/album/%s/index/%%d' % (SPACE, DOMAIN,
			quser.replace('%', '%%'), qalbum.replace('%', '%%'))
	picpat = re.compile(r'imgarr\[len\]={purl:"/%s/album/item/(.+?).html"'
			% (quser,), re.S)
	namepat = re.compile(r'pname:"(.*?)",')
	picurlpat = 'http://%s.%s/%s/pic/item/%%s.jpg' % (PHOTO, DOMAIN,
			quser.replace('%', '%%'))
	lastpage = None
	result = []
	nameresult = []
	for i in xrange(sys.maxint):
		if log: log.write('.')
		r = urllib2.urlopen(urlpat % (i,))
		page = r.read()
		if samepage(page, lastpage):
			break
		result.extend(picpat.findall(page))
		nameresult.extend(namepat.findall(page))
		lastpage = page
	assert len(result) == len(nameresult)
	referer = 'http://%s.%s/%s/album/%s/' % (SPACE, DOMAIN,
			quser.replace('%', '%%'), qalbum.replace('%', '%%'))
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	for i, s, n in zip(xrange(1, sys.maxint), result, nameresult):
		req = urllib2.Request(picurlpat % (s,))
		req.add_header('Referer', referer)
		if not test:
			r = urllib2.urlopen(req)
			f = open(os.path.join(outpath, namingrule % (i,
				pathquote(touni(n)))), 'wb')
			f.write(r.read())
			f.close()
		if log: log.write('.')

if __name__ == '__main__':
	argv = win32_utf8_argv() or sys.argv
	argv = map(lambda s: s.decode('utf-8'), argv)
	if len(argv) < 3:
		print 'Usage: %s command user_name [arguments]' % (os.path.\
				basename(argv[0]),)
		print 'Available commands:'
		print '  l user_name:             list albums of given user'
		print '  d user_name:             download all albums of user'
		print '  d user_name album_name:  download given album of user'
		print '    if album_name starts with dash "-", then it is '\
				'treated as the album index in the list'
		print '  t user_name [album_name]: same as d, but only test, '\
				'do not actually download'
		print 'The download output path is the current directory / '\
				'user_name / album_name, with the exception '\
				'that if the current directory name is '\
				'user_name or album_name, sub directory is '\
				'not created.'
		print 'The naming rule of the downloaded picture is, index + '\
				'dash + picture_name + .jpg, e.g. 1_foo.jpg'
		sys.exit(0)
	try:
		user = argv[2].encode('cp936')
	except:
		user = urllib.unquote(argv[2].encode('utf-8'))
	if len(argv) > 3:
		try:
			album = argv[3].encode('cp936')
		except:
			album = urllib.unquote(argv[3].encode('utf-8'))
	touni = lambda s: s.decode('cp936')
	uuser = touni(user)
	try:
		ar = getalbumlistbyuser(user)
	except:
		print >> sys.stderr, 'Error listing', user
		raise
	if argv[1].lower() == 'l':
		writeunicode(u'User %s has %d albums' % (uuser,
			len(ar)))
		for i, (s, n) in zip(xrange(1, sys.maxint), ar):
			writeunicode(u'%d.\t%s (%d)' % (i, touni(s), n))
	elif argv[1].lower() == 'd' or argv[1].lower() == 't':
		test = argv[1].lower() == 't'
		if len(argv) == 3:
			pardir, curdir = os.path.split(os.getcwdu())
			if curdir == uuser:
				outpath = '.'
			else:
				outpath = pathquote(uuser)
			for s, n in ar:
				ualbum = touni(s)
				writeunicode(u'Downloading %s (%d)' % (
					ualbum, n), newline=False)
				downloadalbum(user, s, outpath=os.path.join(
					outpath, pathquote(ualbum)),
					log=sys.stdout, test=test)
				print
		else:
			idx = None
			if album.startswith('-'):
				try:
					idx = -int(album)-1
				except:
					pass
			if idx is None:
				for i in xrange(len(ar)):
					if ar[i][0] == album:
						idx = i
						break
			if idx is None:
				writeunicode(u'Error determining album %s for '\
						'user %s'%(touni(album), uuser))
				sys.exit(1)
			album = ar[idx][0]
			ualbum = touni(album)
			pardir, curdir = os.path.split(os.getcwdu())
			if curdir == ualbum:
				outpath = '.'
			elif curdir == uuser:
				outpath = pathquote(ualbum)
			else:
				outpath = os.path.join(pathquote(uuser),
						pathquote(ualbum))
			writeunicode(u'Downloading %s (%d)' % (
				ualbum, ar[idx][1]), newline=False)
			downloadalbum(user, album, outpath=outpath,
				log=sys.stdout, test=test)
			print

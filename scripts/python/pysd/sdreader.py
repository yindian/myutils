#!/usr/bin/env python
# Simple StarDict Reader by YIN Dian
# History:
#	2010.02.17.	First version without synonym nor wildcard support
import sys, os, re, string, struct, types
import gzip, dictzip, cStringIO
import pdb, pprint, time

def warn_msg(str, newline=True):
	sys.stdout.flush()
	if newline:
		print >> sys.stderr, str
	else:
		print >> sys.stderr, str,

def info_msg(str, newline=True):
	if newline:
		print str
	else:
		print str,

def parseifo(ifoname):
	f = open(ifoname, 'r')
	try:
		assert f.readline().rstrip() == 'StarDict\'s dict ifo file'
		ifo = dict([line.rstrip().split('=', 1) for line in f.readlines()])
		assert ifo['version'] == '2.4.2'
		assert len(ifo['sametypesequence']) == 1
		wordcount = int(ifo['wordcount'])
		synwordcount = int(ifo.get('synwordcount', '0'))
		idxfilesize = int(ifo['idxfilesize'])
		bookname = ifo['bookname']
	except:
		print >> sys.stderr, 'Error parsing', ifoname
		raise
	f.close()
	return os.path.splitext(ifoname)[0], bookname, idxfilesize, wordcount, synwordcount

def getpossize(wordcount, synwordcount):
	return wordcount * 4

def buildpos(base, idxfilesize, wordcount, synwordcount):
	info_msg('Loading %s.idx...' % (base,))
	f = open(base + '.idx', 'rb')
	idxcontent = f.read()
	assert f.tell() == idxfilesize
	f.close()
	reidx = re.compile(r'.*?\x00.{8}', re.S)
	idxmatches = reidx.findall(idxcontent)
	assert len(idxmatches) == wordcount
	del idxcontent

	info_msg('Writing %s.pos...' % (base,))
	f = open(base + '.pos', 'wb')
	pos = 0
	for record in idxmatches:
		p = record.find('\x00')
		if p >= 192:
			warn_msg('Warning: keyword longer than 200 bytes:', False)
			warn_msg(record[:p])
		f.write(struct.pack('<L', pos))
		pos += len(record)
	f.close()
	del idxmatches
	info_msg('Done building .pos')

def _default_cmp_func(a, b):
	if a == b:
		return 0
	aa = a.lower()
	bb = b.lower()
	if aa == bb:
		return a < b and -1 or 1
	else:
		return aa < bb and -1 or 1

class StarDictReader:
	def __init__(self, ifoname, cmpfunc=None, cachesize=10, bufsize=200):
		inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
		if os.path.exists(inbase + '.idx'):
			self.idxfile = open(inbase + '.idx', 'rb')
		elif os.path.exists(inbase + '.idx.dz'):
			self.idxfile = dictzip.DictzipFile(inbase + '.idx.dz', 'rb')
		elif os.path.exists(inbase + '.idx.gz'):
			self.idxfile = gzip.GzipFile(inbase + '.idx.gz', 'rb')
			buf = self.idxfile.read()
			self.idxfile.close()
			self.idxfile = cStringIO.StringIO(buf)
			del buf
		else:
			raise Exception('Index file not found for ' + inbase)
		if os.path.exists(inbase + '.dict.dz'):
			self.dicfile = dictzip.DictzipFile(inbase + '.dict.dz', 'rb')
		elif os.path.exists(inbase + '.dict'):
			self.dicfile = open(inbase + '.dict', 'rb')
		else:
			raise Exception('Dict file not found for ' + inbase)
		if os.path.exists(inbase + '.pos'):
			self.posfile = open(inbase + '.pos', 'rb')
		else:
			raise Exception('Position file not found for ' + inbase)
		self.name = bookname
		self.wordcount = wordcount # size of posfile / 4
		self.cursor = 0
		self.cmpfunc = cmpfunc or _default_cmp_func
		self.cachesize = cachesize
		self.bufsize = bufsize
		# cache items are (index, word, position) pair
		self._cachekeys = []
		self._cache = {}
		self._cachepos = {}

	def __del__(self):
		self.idxfile.close()
		self.dicfile.close()
		self.posfile.close()

	def _cached_get_word(self, index):
		if index >= self.wordcount or index < 0:
			raise IndexError
		if self._cache.has_key(index):
			return self._cache[index]
		self.posfile.seek(index * 4)
		pos = struct.unpack('<L', self.posfile.read(4))[0]
		self.idxfile.seek(pos)
		buf = self.idxfile.read(self.bufsize)
		p = buf.find('\0')
		if p < 0 or len(buf)-p <= 8:
			buf2 = self.idxfile.read(self.bufsize)
			while buf2:
				buf += buf2
				p = buf.find('\0')
				if p >= 0 and len(buf)-p > 8:
					break
				buf2 = self.idxfile.read(self.bufsize)
		assert p >= 0
		self._cachekeys.append(index)
		self._cache[index] = buf[:p]
		self._cachepos[index] = struct.unpack('!2L', buf[p+1:p+9])
		if len(self._cachekeys) > self.cachesize:
			del self._cache[self._cachekeys[0]]
			del self._cachepos[self._cachekeys[0]]
			del self._cachekeys[0]
		return self._cache[index]

	def _cursor_to_first(self):
		word = self._cached_get_word(self.cursor)
		while self.cursor > 0 and self._cached_get_word(self.cursor-1) == word:
			self.cursor -= 1

	def locate(self, key):
		if type(key) == types.IntType:
			assert 0 <= key < self.wordcount
			self.cursor = key
		else:
			lo = 0
			hi = self.wordcount - 1
			eq = self.wordcount
			for idx in self._cachekeys:
				ltgt = self.cmpfunc(self._cache[idx], key)
				if ltgt < 0 and idx > lo:
					lo = idx
				elif ltgt > 0 and idx < hi:
					hi = idx
				elif ltgt == 0 and idx < eq:
					eq = idx
			if eq < self.wordcount:
				self.cursor = eq
			else:
				while lo < hi:
					mid = (lo + hi) / 2
					if mid == lo:
						lo += 1
					else:
						word = self._cached_get_word(mid)
						ltgt = self.cmpfunc(word, key)
						if ltgt == 0:
							lo = hi = mid
						elif ltgt < 0:
							lo = mid + 1
						else:
							hi = mid - 1
				word = self._cached_get_word(lo)
				ltgt = self.cmpfunc(word, key)
				while ltgt > 0 and lo > 0:
					lo -= 1
					word = self._cached_get_word(lo)
					ltgt = self.cmpfunc(word, key)
				while ltgt < 0 and lo < self.wordcount-1:
					lo += 1
					word = self._cached_get_word(lo)
					ltgt = self.cmpfunc(word, key)
				self.cursor = lo
			self._cursor_to_first()

	def readcursorword(self, advance=1):
		word = self._cached_get_word(self.cursor)
		cursor = self.cursor
		self.cursor += advance
		return word, cursor

	def readcursorwords(self, count=10):
		result = []
		if count > 0:
			advance = 1
		elif count < 0:
			count = -count
			advance = -1
		else:
			return result
		for i in xrange(count):
			try:
				result.append(self.readcursorword(advance))
			except IndexError:
				break
		return result

	def readmean(self, cursor):
		word = self._cached_get_word(cursor)
		pos, length = self._cachepos[cursor]
		self.dicfile.seek(pos)
		return self.dicfile.read(length)

assert __name__ == '__main__'

ioenc = sys.getfilesystemencoding()
debug = True

try:
	from ctypes import windll
	from ctypes.wintypes import DWORD
	STD_OUTPUT_HANDLE = DWORD(-11)
	STD_ERROR_HANDLE = DWORD(-12)
	GetStdHandle = windll.kernel32.GetStdHandle
	WriteConsoleW = windll.kernel32.WriteConsoleW

	def writeunicode(ustr, file, newline=True):
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
	def writeunicode(ustr, file, newline=True):
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

def writetoconsole(ustr, newline=True):
	#if newline:
	#	print ustr.encode(ioenc, 'replace')
	#else:
	#	print ustr.encode(ioenc, 'replace'),
	writeunicode(ustr, sys.stdout, newline)

def showhelp():
	print "Simple Stardict Reader"
	print "Usage: %s [-l] somedict.ifo [more .ifo]" % (os.path.basename(sys.argv[0]), )
	print "   -l: use Latin-1 for lowercase sorting"

if len(sys.argv) == 1 or (sys.argv[1] == '-l' and len(sys.argv) < 3):
	showhelp()
	sys.exit(0)
elif sys.argv[1] == '-l':
	latinsort = True
	flist = sys.argv[2:]
else:
	latinsort = False
	flist = sys.argv[1:]

if latinsort:
	lower = lambda s: unicode(s, 'latin-1').lower().encode('latin-1')
	def cmpfunc(a, b):
		if a == b:
			return 0
		aa = lower(a)
		bb = lower(b)
		if aa == bb:
			return a < b and -1 or 1
		else:
			return aa < bb and -1 or 1
else:
	lower = string.lower
	cmpfunc = None

starttime = time.time()
dictpool = []
for ifoname in flist:
	inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
	if not os.path.exists(inbase + '.pos') or os.stat(inbase + '.pos')[6] != getpossize(wordcount, synwordcount):
		buildpos(inbase, idxfilesize, wordcount, synwordcount)
	dictpool.append(StarDictReader(ifoname, cmpfunc=cmpfunc))
endtime = time.time()
debug and warn_msg('Loading time: %g seconds' % (endtime - starttime,))

def touni(str):
	return unicode(str, 'utf-8')

def selectwords(result, i):
	if not 0 <= i < len(result):
		warn_msg('Wrong selection %d' % (i,))
		return
	writetoconsole(u'[%d]. %s (%s)' % (i, touni(result[i][1]), touni(result[i][2].name)))
	writetoconsole(touni(result[i][2].readmean(result[i][3])))

def showselwords(result):
	if not result:
		return
	for item, i in zip(result, xrange(sys.maxint)):
		writetoconsole(u'[%d]. %s' % (i, touni(item[1])))
	sel = raw_input('Please input your selection (0-%d): ' % (i,))
	try:
		i = int(sel, 0)
	except:
		warn_msg('Wrong selection ' + sel)
		return
	selectwords(result, i)

def forwardresult(dictpool):
	result = []
	for d in dictpool:
		result.extend([(lower(word), word, d, cursor) for word, cursor in d.readcursorwords(10)])
	result.sort()
	visited = {}
	for tmp, word, d, cursor in result[10:]:
		if visited.has_key(id(d)):
			continue
		visited[id(d)] = True
		d.locate(cursor)
	if len(result) >= 10:
		i = 9
	else:
		i = -1
	result[i][2].locate(result[i][3])
	result = result[:10]
	return result

def backwardresult(dictpool):
	result = []
	for d in dictpool:
		result.extend([(lower(word), word, d, cursor) for word, cursor in d.readcursorwords(-10)])
	result.sort()
	visited = {}
	rev = result[:-10]
	rev.reverse()
	for tmp, word, d, cursor in rev:
		if visited.has_key(id(d)):
			continue
		visited[id(d)] = True
		d.locate(cursor)
	if len(result) >= 10:
		i = -10
	else:
		i = 0
	result[i][2].locate(result[i][3])
	result = result[-10:]
	return result

def backwardcursortoend(dictpool, result):
	if not result: return
	for tmp, word, d, cursor in result:
		if d.cursor < cursor:
			d.locate(cursor)
	for d in dictpool:
		try:
			d.locate(d.cursor + 1)
		except:
			pass
	result[-1][2].locate(result[-1][3])

def forwardcursortostart(dictpool, result):
	if not result: return
	for tmp, word, d, cursor in result:
		if d.cursor > cursor:
			d.locate(cursor)
	for d in dictpool:
		try:
			d.locate(d.cursor - 1)
		except:
			pass
	result[0][2].locate(result[0][3])

result = None
lastkey = None
lastdir = 1
while True:
	try:
		cmd = raw_input('>')
	except EOFError:
		break
	if cmd.startswith('/'):
		ar = cmd.split()
		ar[0] = ar[0].lower()
		if ar[0] in ('/q', '/quit'):
			break
		elif len(ar[0]) == 2 and ar[0][1] in string.digits and result:
			selectwords(result, int(ar[0][1:]))
		elif ar[0] in ('/l', '/list'):
			try:
				showselwords(result)
			except EOFError:
				break
		elif ar[0] in ('/n', '/next', '/f', '/forward') and lastkey is not None:
			if lastdir < 0:
				backwardcursortoend(dictpool, result)
			if len(ar) > 1:
				try:
					for i in xrange(int(ar[1], 0)-1):
						forwardresult(dictpool)
				except ValueError:
					pass
			result = forwardresult(dictpool)
			lastdir = 1
			try:
				showselwords(result)
			except EOFError:
				break
		elif ar[0] in ('/p', '/previous', '/b', '/backward') and lastkey is not None:
			if lastdir > 0:
				forwardcursortostart(dictpool, result)
			if len(ar) > 1:
				try:
					for i in xrange(int(ar[1], 0)-1):
						backwardresult(dictpool)
				except ValueError:
					pass
			result = backwardresult(dictpool)
			lastdir = -1
			try:
				showselwords(result)
			except EOFError:
				break
	else:
		key = unicode(cmd, ioenc).encode('utf-8')
		for d in dictpool:
			d.locate(key)
		result = forwardresult(dictpool)
		lastkey = key
		lastdir = 1
		showselwords(result)

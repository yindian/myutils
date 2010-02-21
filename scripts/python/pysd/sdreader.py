#!/usr/bin/env python
# Simple StarDict Reader by YIN Dian
# History:
#	2010.02.17.	First version without synonym nor wildcard support
#	2010.02.18.	Second version with synonym support
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

def _default_cmp_func(a, b):
	if a == b:
		return 0
	aa = a.lower()
	bb = b.lower()
	if aa == bb:
		return a < b and -1 or 1
	else:
		return aa < bb and -1 or 1

def getpossize(wordcount, synwordcount):
	return (wordcount + synwordcount) * 4

def buildpos(base, idxfilesize, wordcount, synwordcount, cmpfunc=_default_cmp_func):
	info_msg('Loading %s.idx...' % (base,))
	try:
		f = open(base + '.idx', 'rb')
	except IOError:
		f = gzip.GzipFile(base + '.idx.gz', 'rb')
	idxcontent = f.read()
	assert f.tell() == idxfilesize
	assert idxfilesize <= 0x80000000L
	f.close()
	reidx = re.compile(r'.*?\x00.{8}', re.S)
	idxmatches = reidx.findall(idxcontent)
	assert len(idxmatches) == wordcount
	del idxcontent

	if synwordcount > 0:
		info_msg('Loading %s.syn...' % (base,))
		try:
			f = open(base + '.syn', 'rb')
		except IOError:
			f = gzip.GzipFile(base + '.syn.gz', 'rb')
		syncontent = f.read()
		f.close()
		resyn = re.compile(r'.*?\x00.{4}', re.S)
		synmatches = resyn.findall(syncontent)
		assert len(synmatches) == synwordcount
		del syncontent
	else:
		synmatches = []

	info_msg('Writing %s.pos...' % (base,))
	f = open(base + '.pos', 'wb')
	pos = 0
	synpos = 0
	synidx = 0
	for record in idxmatches:
		p = record.find('\x00')
		if p >= 192:
			warn_msg('Warning: keyword longer than 200 bytes:', False)
			warn_msg(record[:p])
		while synidx < synwordcount:
			q = synmatches[synidx].find('\x00')
			if p >= 192:
				warn_msg('Warning: syn keyword longer than 200 bytes:', False)
				warn_msg(synmatches[synidx][:q])
			if cmpfunc(synmatches[synidx][:q], record[:p]) < 0:
				f.write(struct.pack('<L', synpos | 0x80000000L))
				synpos += len(synmatches[synidx])
				synidx += 1
			else:
				break
		f.write(struct.pack('<L', pos))
		pos += len(record)
	while synidx < synwordcount:
		q = synmatches[synidx].find('\x00')
		if p >= 192:
			warn_msg('Warning: syn keyword longer than 200 bytes:', False)
			warn_msg(synmatches[synidx][:q])
		f.write(struct.pack('<L', synpos | 0x80000000L))
		synpos += len(synmatches[synidx])
		synidx += 1
	f.close()
	del idxmatches
	info_msg('Done building .pos')

class StarDictReader:
	def __init__(self, ifoname, cmpfunc=None, cachesize=10, bufsize=200):
		inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
		assert 0 < idxfilesize <= 0x80000000L
		assert 0 < wordcount
		assert 0 <= synwordcount
		if os.path.exists(inbase + '.idx'):
			self.idxfile = open(inbase + '.idx', 'rb')
		elif os.path.exists(inbase + '.idx.gz'):
			self.idxfile = gzip.GzipFile(inbase + '.idx.gz', 'rb')
			buf = self.idxfile.read()
			self.idxfile.close()
			self.idxfile = cStringIO.StringIO(buf)
			del buf
		else:
			raise Exception('Index file not found for ' + inbase)
		if synwordcount > 0:
			if os.path.exists(inbase + '.syn'):
				self.synfile = open(inbase + '.syn', 'rb')
			elif os.path.exists(inbase + '.syn.gz'):
				self.synfile = gzip.GzipFile(inbase + '.syn.gz', 'rb')
				buf = self.synfile.read()
				self.synfile.close()
				self.synfile = cStringIO.StringIO(buf)
				del buf
			else:
				raise Exception('Synonym file not found for ' + inbase)
		else:
			self.synfile = None
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
		self.wordcount = wordcount + synwordcount # size of posfile / 4
		self.maxsynidx = wordcount
		self.cursor = 0
		self.cmpfunc = cmpfunc or _default_cmp_func
		self.cachesize = cachesize
		self.syncachesize = cachesize * 1
		self.bufsize = bufsize
		# cache items are (index, word, position) pair
		self._cachekeys = []
		self._cache = {}
		self._cachepos = {}
		# syn cache items are (index, syncount) pair
		self._cachesyn = []

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
		if pos < 0x80000000L:
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
		else: # synonym
			pos &= 0x7FFFffffL
			self.synfile.seek(pos)
			buf = self.synfile.read(self.bufsize)
			p = buf.find('\0')
			if p < 0 or len(buf)-p <= 4:
				buf2 = self.synfile.read(self.bufsize)
				while buf2:
					buf += buf2
					p = buf.find('\0')
					if p >= 0 and len(buf)-p > 4:
						break
					buf2 = self.synfile.read(self.bufsize)
			assert p >= 0
			self._cachekeys.append(index)
			self._cache[index] = buf[:p]
			self._cachepos[index] = struct.unpack('!L', buf[p+1:p+5])
		if len(self._cachekeys) > self.cachesize:
			del self._cache[self._cachekeys[0]]
			del self._cachepos[self._cachekeys[0]]
			del self._cachekeys[0]
		return self._cache[index]

	def _cached_synidx_to_cursor(self, synidx):
		# index:   0 1 2 3 4 5 6 7 8 9 A B C D E F
		# pos&MSB: 0 0 0 1 0 0 1 0 0 0 1 1 0 0 1 0
		# syncnt:  0 0 0 1 1 1 2 2 2 2 3 4 4 4 5 5
		# idxidx:  0 1 2 2 3 4 4 5 6 7 7 7 8 9 9 A
		assert 0 <= synidx < self.maxsynidx
		cur = 0
		cnt = 0
		dir = 1
		for idx, syncnt in self._cachesyn:
			idxidx = idx - syncnt
			if idxidx < synidx:
				cur = idx + 1
				cnt = syncnt
				dir = 1
			elif idxidx == synidx:
				cur = idx
				cnt = syncnt
				dir = -1
				return cur # _cachesyn doesn't store pos&MSB !=0
			else:
				break
		if dir < 0:
			while cur - cnt == synidx:
				self.posfile.seek(cur * 4)
				pos = struct.unpack('<L', self.posfile.read(4))[0]
				cur -= 1
				if pos >= 0x80000000L:
					cnt -= 1
		self.posfile.seek(cur * 4)
		while cur - cnt < synidx:
			pos = struct.unpack('<L', self.posfile.read(4))[0]
			cur += 1
			if pos >= 0x80000000L:
				cnt += 1
		i = 0
		for i in xrange(len(self._cachesyn)):
			if self._cachesyn[i][0] >= cur:
				break
		if i < len(self._cachesyn) and self._cachesyn[i][0] < cur:
			i += 1
		self._cachesyn.insert(i, (cur, cnt))
		k = i
		if len(self._cachesyn) > self.syncachesize:
			mindiff = sys.maxint
			mini = -1
			for i in xrange(len(self._cachesyn)-1):
				if i+1 != k and self._cachesyn[i+1][0] - self._cachesyn[i][0] < mindiff:
					mindiff = self._cachesyn[i+1][0] - self._cachesyn[i][0]
					mini = i
			assert mini >= 0
			del self._cachesyn[mini+1]
		return cur

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

	def derefsyncursor(self, cursor):
		word = self._cached_get_word(cursor)
		if len(self._cachepos[cursor]) == 2:
			return cursor
		else: # synonym
			return self._cached_synidx_to_cursor(self._cachepos[cursor][0])

	def readword(self, cursor):
		return self._cached_get_word(cursor)

	def readmean(self, cursor):
		cursor = self.derefsyncursor(cursor)
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
	print "Usage: %s [-l] [-b] somedict.ifo [more .ifo]" % (os.path.basename(sys.argv[0]), )
	print "   -l: use Latin-1 for lowercase sorting"
	print "   -b: build auxiliary files only"

if len(sys.argv) == 1 or (sys.argv[1] == '-l' and len(sys.argv) < 3):
	showhelp()
	sys.exit(0)
elif sys.argv[1] == '-l':
	latinsort = True
	flist = sys.argv[2:]
else:
	latinsort = False
	flist = sys.argv[1:]

if flist[0] == '-b':
	buildonly = True
	flist = flist[1:]
else:
	buildonly = False

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
	if not os.path.exists(inbase + '.pos') or os.stat(inbase + '.pos')[6] != getpossize(wordcount, synwordcount
		) or os.stat(inbase + '.pos')[-2] < os.stat(inbase + '.ifo')[-2]:
		buildpos(inbase, idxfilesize, wordcount, synwordcount)
	dictpool.append(StarDictReader(ifoname, cmpfunc=cmpfunc))
endtime = time.time()
debug and warn_msg('Loading time: %g seconds' % (endtime - starttime,))

if buildonly:
	sys.exit(0)

def touni(str):
	return unicode(str, 'utf-8')

def selectwords(result, i):
	if not 0 <= i < len(result):
		warn_msg('Wrong selection %d' % (i,))
		return
	cursor = result[i][2].derefsyncursor(result[i][3])
	writetoconsole(u'[%d]. %s (%s' % (i, touni(result[i][1]), touni(result[i][2].name)) +
	(cursor == result[i][3] and u')' or u') => %s' % (touni(result[i][2].readword(cursor)))))
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

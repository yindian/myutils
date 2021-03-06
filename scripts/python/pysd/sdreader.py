#!/usr/bin/env python
# Simple StarDict Reader by YIN Dian
# History:
#	2010.02.17.	First version without synonym nor wildcard support
#	2010.02.18.	Second version with synonym support
#			Build trie for wildcard support
#	2010.03.28.	Serialize trie and query wildcard (10%)
import sys, os, re, string, struct, types
import gzip, dictzip, cStringIO
import pdb, pprint, time
import traceback

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

def _get_word_by_cursor(cursorarray, idxmatches, synmatches, cursor):
	idx = cursorarray[cursor]
	if idx >= 0:
		return idxmatches[idx]
	else:
		return synmatches[-idx - 1]

def _getalphabetlist(cursorarray, idxmatches, synmatches, depth, low, high):
	visited = {}
	queue = [(low, high)] # all words between (low, high) shall have len > depth
	while queue:
		lo, hi = queue.pop() # order no matter, pop last is stack
		loword = _get_word_by_cursor(cursorarray, idxmatches, synmatches, lo)
		loch = loword[depth]
		if not visited.has_key(loch) or visited[loch] > lo:
			visited[loch] = lo
		if lo < hi-1:
			hiword = _get_word_by_cursor(cursorarray, idxmatches, synmatches, hi-1)
			hich = hiword[depth]
			if not visited.has_key(hich) or visited[hich] > hi-1:
				visited[hich] = hi-1
			mid = (lo + hi) / 2
			midword = _get_word_by_cursor(cursorarray, idxmatches, synmatches, mid)
			midch = midword[depth]
			if mid < hi-1 and midch != hich:
				queue.append((mid, hi-1))
			elif not visited.has_key(midch) or visited[midch] > mid:
				visited[midch] = mid
			if mid > lo and midch != loch:
				queue.append((lo+1, mid))
	result = visited.items()
	result.sort()
	for i in xrange(len(result)):
		assert _get_word_by_cursor(cursorarray, idxmatches, synmatches, result[i][1])[depth] == result[i][0]
		if i > 1:
			assert _get_word_by_cursor(cursorarray, idxmatches, synmatches, result[i][1]-1)[depth] == result[i-1][0]
	return result

def _reversesort(reversedword, depth, low, high):
	#st = time.time()
	result = []
	for i in xrange(low, high):
		#word = reversedword[i][:-depth] or reversedword[i]
		#result.append((word, i))
		result.append((reversedword[i], i))
	#info_msg('Reverse sort middle %g seconds' % (time.time() - st,))
	result.sort()
	#info_msg('Reverse sort middle 2 %g seconds' % (time.time() - st,))
	result = [b for a, b in result]
	#result = range(low, high)
	#result.sort(lambda a, b: reversedword[a] < reversedword[b] and -1 or (reversedword[a] > reversedword[b] and 1 or 0))
	#info_msg('Reverse sort (%d, %d) costs %g seconds' % (low, high, time.time() - st,))
	return result

def buildtrie(cursorarray, idxmatches, synmatches, reversedword, path, low, high, minchldnum=2048):
	depth = len(path)
	# node value, exact match / all range, children, reverse sorted list
	#info_msg('Enter buildtrie for "%s" (%d, %d)' % (path, low, high))
	result = [None, [low], [], _reversesort(reversedword, depth, low, high)]
	while low < high and _get_word_by_cursor(cursorarray, idxmatches, synmatches, low) == path:
		low += 1
	result[1].append(low)
	result[1].append(high)
	if high - low > minchldnum:
		#st = time.time()
		alphabet = _getalphabetlist(cursorarray, idxmatches, synmatches, len(path), low, high)
		#info_msg('Get alphabet list for "%s" costs %g seconds' % (path, time.time() - st,))
		assert alphabet
		for i in xrange(len(alphabet)-1):
			result[2].append(buildtrie(cursorarray, idxmatches, synmatches, reversedword,
					path + alphabet[i][0], alphabet[i][1], alphabet[i+1][1], minchldnum))
			result[2][-1][0] = alphabet[i][0]
		result[2].append(buildtrie(cursorarray, idxmatches, synmatches, reversedword,
				path + alphabet[-1][0], alphabet[-1][1], high, minchldnum))
		result[2][-1][0] = alphabet[-1][0]
	return result

def serializetrie(node, path=''):
	# one node costs 4*4 bytes plus reverse sorted list
	#   node value char, control byte, 16-bit sub node count,                // 1st 4 bytes
	#   exact match count, high boundary index (low boundary is implied),    // next 8 bytes
	#   reversed sort list offset (starting from beginning of file)          // last 4 bytes

	#print `path`.rjust(len(path)*4), node[1]
	noderesult = [[node[0] or '\0', 0, 0, node[1][1] - node[1][0], node[1][2], path]]
	revlists = [node[-1]]
	for n in node[2]:
		subnodes, subrevlists = serializetrie(n, path+n[0])
		noderesult.extend(subnodes)
		revlists.extend(subrevlists)
	if len(noderesult) > 0x10000:
		raise Exception('Too many (%d) sub nodes for %s' % (len(noderesult)-1, path))
	noderesult[0][2] = len(noderesult) - 1
	if path:
		return noderesult, revlists
	else:
		assert node[0] is None
		assert len(noderesult) == len(revlists)
		result = []
		offset = len(noderesult) * 16
		i = 0
		for value, flag, subcnt, matcnt, highidx, tmp in noderesult:
			result.append(struct.pack('<cBHLLL', value, flag, subcnt, matcnt, highidx, offset))
			offset += len(revlists[i]) * 4
			i += 1
		for rev in revlists:
			result.append(struct.pack('<' + 'L'*len(rev), *rev))
		result = ''.join(result)
		assert len(result) == offset
		return result

def getpossize(wordcount, synwordcount):
	return (wordcount + synwordcount) * 4

def checkwcdfile(wcdfname, wordcount, synwordcount):
	try:
		f = open(wcdfname, 'rb')
		buf = f.read(16)
		value, flag, subcnt, matcnt, highidx, offset = struct.unpack('<cBHLLL', buf)
		assert highidx == wordcount + synwordcount
		k = offset
		lowidx = 0
		# find last node
		while subcnt:
			p = highidx
			# first child
			buf = f.read(16)
			value, flag, subcnt, matcnt, highidx, offset = struct.unpack('<cBHLLL', buf)
			while highidx < p:
				lowidx = highidx
				# next child
				f.seek(subcnt * 16, 1)
				buf = f.read(16)
				value, flag, subcnt, matcnt, highidx, offset = struct.unpack('<cBHLLL', buf)
		assert f.tell() == k
		f.seek(offset)
		buf = f.read((highidx - lowidx) * 4)
		assert len(buf) == (highidx - lowidx) * 4
		k = f.tell()
		f.seek(0, 2)
		assert f.tell() == k
		f.close()
	except Exception, e:
		print >> sys.stderr, 'Invalid %s: %s' % (wcdfname, `e`)
		traceback.print_exc()
		f.close()
		return False
	return True

def buildposwcd(base, idxfilesize, wordcount, synwordcount, cmpfunc, lwrfunc):
	global starttime
	info_msg('Loading %s.idx...\t%.4gs' % (base, time.time() - starttime))
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
		info_msg('Loading %s.syn...\t%.4gs' % (base, time.time() - starttime))
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

	info_msg('Writing %s.pos...\t%.4gs' % (base, time.time() - starttime))
	f = open(base + '.pos', 'wb')
	pos = 0
	synpos = 0
	synidx = 0
	cursorarray = []
	cachedsynidx = None
	reversedword = []
	for idx in xrange(len(idxmatches)):
		p = idxmatches[idx].find('\x00')
		word = idxmatches[idx][:p]
		if p >= 192:
			warn_msg('Warning: keyword longer than 200 bytes:', False)
			warn_msg(word)
		while synidx < synwordcount:
			if cachedsynidx != synidx:
				q = synmatches[synidx].find('\x00')
				synword = synmatches[synidx][:q]
				if q >= 192:
					warn_msg('Warning: syn keyword longer than 200 bytes:', False)
					warn_msg(synword)
				cachedsynidx = synidx
			if cmpfunc(synword, word) < 0:
				f.write(struct.pack('<L', synpos | 0x80000000L))
				cursorarray.append(-synidx - 1)
				synpos += len(synmatches[synidx])
				synmatches[synidx] = lwrfunc(synword)
				reversedword.append(synmatches[synidx])
				synidx += 1
			else:
				break
		f.write(struct.pack('<L', pos))
		cursorarray.append(idx)
		pos += len(idxmatches[idx])
		idxmatches[idx] = lwrfunc(word)
		reversedword.append(idxmatches[idx])
	while synidx < synwordcount:
		q = synmatches[synidx].find('\x00')
		if q >= 192:
			warn_msg('Warning: syn keyword longer than 200 bytes:', False)
			warn_msg(synmatches[synidx][:q])
		f.write(struct.pack('<L', synpos | 0x80000000L))
		cursorarray.append(-synidx - 1)
		synpos += len(synmatches[synidx])
		synmatches[synidx] = lwrfunc(synmatches[synidx][:q])
		reversedword.append(synmatches[synidx])
		synidx += 1
	f.close()
	info_msg('Done building .pos\t\t%.4gs' % (time.time() - starttime,))
	assert len(cursorarray) == wordcount + synwordcount == len(reversedword)
	info_msg('Building reversed words...\t%.4gs' % (time.time() - starttime,))
	for i in xrange(len(reversedword)):
		ar = list(reversedword[i])
		ar.reverse()
		reversedword[i] = ''.join(ar)
	info_msg('Building wildcard tier...\t%.4gs' % (time.time() - starttime,))
	root = buildtrie(cursorarray, idxmatches, synmatches, reversedword, '', 0, len(cursorarray)) # totally ignore case
	info_msg('Writing %s.wcd...\t%.4gs' % (base, time.time() - starttime))
	f = open(base + '.wcd', 'wb')
	f.write(serializetrie(root))
	f.close()
	info_msg('Done building .wcd\t\t%.4gs' % (time.time() - starttime,))
	del idxmatches
	del synmatches

class StarDictReaderBase:
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

	def getcursor(self):
		return self.cursor

def haswildcard(key):
	return key.find('*') >= 0 or key.find('?') >= 0

def _matchquestionmark(word, pattern):
	if len(word) != len(pattern):
		return False
	for i in xrange(len(word)):
		if pattern[i] != u'?' and not word[i] == pattern[i]:
			return False
	return True

def _findbyquestionmark(word, pattern, start=0):#, end=-1):
	#if end < 0:
	#	end += len(word)
	if len(word) < len(pattern):
		return -1
	elif len(word) == len(pattern):
		if _matchquestionmark(word, pattern):
			return 0
		else:
			return -1
	ar = pattern.split(u'?')
	for k in xrange(start, len(word) - len(pattern) + 1):
		i = k
		match = True
		for snip in ar:
			if snip and word[i:i+len(snip)] != snip:
				match = False
				break
			i += len(snip) + 1
		if match:
			return k
	return -1

def matchwildcard(word, pattern, lwrfunc=string.lower):
	#assert type(pattern) == types.UnicodeType
	if type(word) != types.UnicodeType:
		word = word.decode('utf-8')
	if type(pattern) != types.UnicodeType:
		pattern = pattern.decode('utf-8')
	word = lwrfunc(word)
	pattern = lwrfunc(pattern)
	if pattern.find(u'*') < 0:
		return _matchquestionmark(word, pattern)
	ar = pattern.split(u'*')
	if ar[0] and not _matchquestionmark(word[:len(ar[0])], ar[0]):
		return False
	elif ar[-1] and not _matchquestionmark(word[-len(ar[-1]):], ar[-1]):
		_matchquestionmark(word[-len(ar[-1]):], ar[-1])
		return False
	p = len(ar[0])
	for i in xrange(1, len(ar)):
		if ar[i] == u'': continue
		q = word.find(ar[i], p)
		if q < 0:
			if ar[i].find(u'?') >= 0:
				q = _findbyquestionmark(word, ar[i], p)
			if q < 0:
				return False
		p = q + len(ar[i])
	return True

class StarDictReader(StarDictReaderBase):
	def __init__(self, ifoname, cmpfunc=None, cachesize=10, bufsize=200):
		StarDictReaderBase.__init__(self, ifoname, cmpfunc=cmpfunc, cachesize=cachesize, bufsize=bufsize)
		self.lastqry = None
		self.lastwild = False
		self.wildcursor = 0

	def locate(self, key):
		if type(key) == types.IntType:
			if not self.lastwild:
				return StarDictReaderBase.locate(self, key)
			else:
				pass
		else:
			if not haswildcard(key):
				self.lastwild = False
				self.lastqry = key.decode('utf-8')
				return StarDictReaderBase.locate(self, key)
			self.lastwild = True
			self.lastqry = key.decode('utf-8')

	def readcursorword(self, advance=1):
		return StarDictReaderBase.readcursorword(self, advance)

	def readcursorwords(self, count=10):
		return StarDictReaderBase.readcursorwords(self, count)

	def derefsyncursor(self, cursor):
		return StarDictReaderBase.derefsyncursor(self, cursor)

	def readword(self, cursor):
		return StarDictReaderBase.readword(self, cursor)

	def readmean(self, cursor):
		return StarDictReaderBase.readmean(self, cursor)

	def getcursor(self):
		if not self.lastwild:
			return StarDictReaderBase.getcursor(self)
		else:
			return self.wildcursor

assert __name__ == '__main__'

ioenc = sys.getfilesystemencoding()
debug = True

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
	latinlwrmap = string.maketrans(string.ascii_uppercase + ''.join(map(chr, range(0xc0, 0xd7) +
	range(0xd8, 0xdf))), string.ascii_lowercase + ''.join(map(chr, range(0xe0, 0xf7) + range(
	0xf8, 0xff))))
	lower = lambda s: s.translate(latinlwrmap)
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
	cmpfunc = _default_cmp_func

starttime = time.time()
dictpool = []
for ifoname in flist:
	inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
	if not os.path.exists(inbase + '.pos') or os.stat(inbase + '.pos')[6] != getpossize(wordcount, synwordcount
		) or os.stat(inbase + '.pos')[-2] < os.stat(inbase + '.ifo')[-2] or not os.path.exists(inbase + '.wcd'
		) or not checkwcdfile(inbase + '.wcd', wordcount, synwordcount
		) or os.stat(inbase + '.wcd')[6] == 0 or os.stat(inbase + '.wcd')[-2] < os.stat(inbase + '.ifo')[-2]:
		buildposwcd(inbase, idxfilesize, wordcount, synwordcount, cmpfunc=cmpfunc, lwrfunc=lower)
	dictpool.append(StarDictReader(ifoname, cmpfunc=cmpfunc))
endtime = time.time()
debug and warn_msg('Loading time: %g seconds' % (endtime - starttime,))

if buildonly:
	sys.exit(0)

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
		if d.getcursor() < cursor:
			d.locate(cursor)
	for d in dictpool:
		try:
			d.locate(d.getcursor() + 1)
		except:
			pass
	result[-1][2].locate(result[-1][3])

def forwardcursortostart(dictpool, result):
	if not result: return
	for tmp, word, d, cursor in result:
		if d.getcursor() > cursor:
			d.locate(cursor)
	for d in dictpool:
		try:
			d.locate(d.getcursor() - 1)
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

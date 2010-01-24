#!/usr/bin/env python
import sys, string, struct, os.path, getopt, gzip, re

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

def getmarker(inbase, bookname):
	return '<--- %s --->\n' % (bookname,)

def getmergedkey(word, syn):
	return '%s (%s)\n' % (word, ', '.join(syn))

def getsynredirct(word, syn):
	return '#=> %s' % (word,)

def getseparator():
	return '\n\n'

def flushindex(outbase, index):
	print >> sys.stderr, 'Writing index...'
	index.sort()

	idxfile = open(outbase + '.idx', 'wb')
	synlist = []
	for idx, (tmp, word, offset, length, syn) in zip(xrange(len(index)), index):
		idxfile.write(word)
		idxfile.write('\0')
		idxfile.write(struct.pack('>LL', offset, length))
		for s in syn:
			synlist.append((s.lower(), s, idx))

	if len(synlist) > 0:
		print >> sys.stderr, 'Writing synonym...'
		synlist.sort()
		synfile = open(outbase + '.syn', 'wb')
		for tmp, syn, idx in synlist:
			synfile.write(syn)
			synfile.write('\0')
			synfile.write(struct.pack('>L', idx))

	print >> sys.stderr, 'Writing dict info...'
	ifofile = open(outbase + '.ifo', 'wb')

	bookname = outbase
	typeseq = 'm'

	if len(synlist) > 0:
		ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nsynwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(index), len(synlist), idxfile.tell(), bookname, typeseq))
	else:
		ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(index), idxfile.tell(), bookname, typeseq))

	idxfile.close()
	ifofile.close()
	if len(synlist) > 0: synfile.close()

assert __name__ == '__main__'

opts, args = getopt.getopt(sys.argv[1:], 'msd:th', ['help'])
opts = dict(opts)
if len(args) < 2 or opts.has_key('-h') or opts.has_key('--help'):
	print "Usage: %s [-m] [-s] [-d maxdictsize] [-t] ifofile(s) outbase" % (sys.argv[0])
	print "Merge or decompile multiple stardict dictionaries to one"
	print "Options:"
	print "-m:\tmerge keywords and synonyms"
	print "-d:\tdereference synonyms when merge (-m)"
	print "-d:\tset maximum .dict file size"
	print "-t:\toutput tabfile source"
	sys.exit(0)
maxdictsize = int(opts.get('-d', '0')) or (1 << 31) - 1
mergekey = opts.has_key('-m')
derefsyn = opts.has_key('-s')
textout = opts.has_key('-t')
outbase = args[-1]

dictcnt = 0
index = []

if textout:
	txtfile = open(outbase + '.txt', 'w')
else:
	dicfile = open(outbase + '.dict', 'wb')

idxre = re.compile('.*?\0.{8}', re.S)
synre = re.compile('.*?\0.{4}', re.S)

if not mergekey: # no need to reorder mean
	print >> sys.stderr, 'Writing data...'
	for ifoname in args[:-1]:
		inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
		if os.path.exists(inbase + '.idx.gz'):
			f = gzip.GzipFile(inbase + '.idx.gz', 'rb')
			fname = inbase + '.idx.gz'
		else:
			f = open(inbase + '.idx', 'rb')
			fname = inbase + '.idx'
		print >> sys.stderr, 'Reading %s...' % (fname,)
		findex = []
		rawindex = idxre.findall(f.read())
		try:
			assert len(rawindex) == wordcount
			assert f.tell() == idxfilesize
		except:
			print >> sys.stderr, 'Error validating', fname
			raise
		f.close()
		for item in rawindex:
			p = item.index('\0')
			word = item[:p]
			offset, length = struct.unpack('>LL', item[p+1:])
			findex.append([offset, length, word, []])
		del rawindex
		if synwordcount > 0:
			fname = inbase + '.syn'
			f = open(fname, 'rb')
			print >> sys.stderr, 'Reading %s...' % (fname,)
			rawsynonym = synre.findall(f.read())
			f.close()
			try:
				assert len(rawsynonym) == synwordcount
			except:
				print >> sys.stderr, 'Error validating', fname
				raise
			for item in rawsynonym:
				p = item.index('\0')
				syn = item[:p]
				(idx,) = struct.unpack('>L', item[p+1:])
				findex[idx][-1].append(syn)
			del rawsynonym
		#continue
		findex.sort()
		if os.path.exists(inbase + '.dict.dz'):
			f = gzip.GzipFile(inbase + '.dict.dz', 'rb')
			fname = inbase + '.dict.dz'
		else:
			f = open(inbase + '.dict', 'rb')
			fname = inbase + '.dict'
		print >> sys.stderr, 'Reading %s...' % (fname,)
		if textout:
			for offset, length, word, syn in findex:
				assert f.tell() == offset
				mean = f.read(length).replace('\\n', '\\\\n').replace('\n', '\\n')
				print >> txtfile, '%s\t%s' % ('|'.join([word] + syn), mean)
		else:
			for offset, length, word, syn in findex:
				assert f.tell() == offset
				mean = f.read(length)
				offset_old = dicfile.tell()
				if offset_old + len(mean) > maxdictsize:
					dicfile.close()
					if dictcnt == 0:
						flushindex(outbase, index)
					else:
						flushindex(outbase+str(dictcnt), index)
					dictcnt += 1
					dicfile = open(outbase+str(dictcnt) + '.dict', 'wb')
					print >> sys.stderr, 'Writing data %d...' % (dictcnt,)
					index = []
					offset_old = dicfile.tell()
				dicfile.write(mean)
				index.append((word.lower(), word, offset_old, length, syn))
		f.close()
else: # read all indices in memory and sort
	bigindex = []
	dictfiles = {}
	for ifoname in args[:-1]:
		inbase, bookname, idxfilesize, wordcount, synwordcount = parseifo(ifoname)
		if os.path.exists(inbase + '.idx.gz'):
			f = gzip.GzipFile(inbase + '.idx.gz', 'rb')
			fname = inbase + '.idx.gz'
		else:
			f = open(inbase + '.idx', 'rb')
			fname = inbase + '.idx'
		print >> sys.stderr, 'Reading %s...' % (fname,)
		findex = []
		rawindex = idxre.findall(f.read())
		try:
			assert len(rawindex) == wordcount
			assert f.tell() == idxfilesize
		except:
			print >> sys.stderr, 'Error validating', fname
			raise
		f.close()
		for item in rawindex:
			p = item.index('\0')
			word = item[:p]
			offset, length = struct.unpack('>LL', item[p+1:])
			findex.append([offset, length, word, []])
		del rawindex
		if synwordcount > 0:
			fname = inbase + '.syn'
			f = open(fname, 'rb')
			print >> sys.stderr, 'Reading %s...' % (fname,)
			rawsynonym = synre.findall(f.read())
			f.close()
			try:
				assert len(rawsynonym) == synwordcount
			except:
				print >> sys.stderr, 'Error validating', fname
				raise
			for item in rawsynonym:
				p = item.index('\0')
				syn = item[:p]
				(idx,) = struct.unpack('>L', item[p+1:])
				findex[idx][-1].append(syn)
			del rawsynonym
		for offset, length, word, syn in findex:
			bigindex.append((word, inbase, offset, length, bookname, syn))
			for i in xrange(len(syn)):
				ar = syn[:]
				del ar[i]
				if derefsyn:
					bigindex.append((syn[i], inbase, offset, length, bookname, [word]+ar))
				else:
					bigindex.append((syn[i], inbase, None, None, bookname, [word]+ar))
		if os.path.exists(inbase + '.dict.dz'):
			f = gzip.GzipFile(inbase + '.dict.dz', 'rb')
			print >> sys.stderr, 'Warning: dictzip random access not implemented. Seeking is extremely slow for', inbase+'.dict.dz'
		else:
			f = open(inbase + '.dict', 'rb')
		dictfiles[inbase] = f
	print >> sys.stderr, 'Sorting data...'
	bigindex.sort()
	print >> sys.stderr, 'Writing data...'
	lastword = None
	lastbase = None
	if textout:
		for word, inbase, offset, length, bookname, syn in bigindex:
			f = dictfiles[inbase]
			if offset is not None:
				f.seek(offset)
			if lastword != word:
				if lastword is not None:
					print >> txtfile
				txtfile.write('%s\t' % (word,))
				lastbase = None
				mean = []
			else:
				mean = [getseparator()]
			if lastbase != inbase and len(args) > 2:
				mean.append(getmarker(inbase, bookname))
			if not derefsyn:
				mean.append(getmergedkey(word, syn))
			if length is not None:
				mean.append(f.read(length))
			else:
				mean.append(getsynredirct(syn[0], [word]+syn[1:]))
			mean = ''.join(mean).replace('\\n', '\\\\n').replace('\n', '\\n')
			txtfile.write(mean)
			lastword = word
			lastbase = inbase
		if lastword is not None:
			print >> txtfile
	else:
		for word, inbase, offset, length, bookname, syn in bigindex:
			f = dictfiles[inbase]
			if offset is not None:
				f.seek(offset)
			if lastword is None:
				lastbase = None
				mean = []
			elif lastword != word:
				offset_old = dicfile.tell()
				mean = ''.join(mean)
				if offset_old + len(mean) > maxdictsize:
					dicfile.close()
					if dictcnt == 0:
						flushindex(outbase, index)
					else:
						flushindex(outbase+str(dictcnt), index)
					dictcnt += 1
					dicfile = open(outbase+str(dictcnt) + '.dict', 'wb')
					print >> sys.stderr, 'Writing data %d...' % (dictcnt,)
					index = []
					offset_old = dicfile.tell()
				dicfile.write(mean)
				index.append((lastword.lower(), lastword, offset_old, len(mean), []))
				lastbase = None
				mean = []
			else:
				mean.append(getseparator())
			if lastbase != inbase and len(args) > 2:
				mean.append(getmarker(inbase, bookname))
			if not derefsyn:
				mean.append(getmergedkey(word, syn))
			if length is not None:
				mean.append(f.read(length))
			else:
				mean.append(getsynredirct(syn[0], [word]+syn[1:]))
			lastword = word
			lastbase = inbase
		if lastword is not None: # flush last word
			offset_old = dicfile.tell()
			mean = ''.join(mean)
			if offset_old + len(mean) > maxdictsize:
				dicfile.close()
				if dictcnt == 0:
					flushindex(outbase, index)
				else:
					flushindex(outbase+str(dictcnt), index)
				dictcnt += 1
				dicfile = open(outbase+str(dictcnt) + '.dict', 'wb')
				print >> sys.stderr, 'Writing data %d...' % (dictcnt,)
				index = []
				offset_old = dicfile.tell()
			dicfile.write(mean)
			index.append((lastword.lower(), lastword, offset_old, len(mean), []))
	for f in dictfiles.itervalues():
		f.close()

if textout:
	txtfile.close()
else:
	dicfile.close()
	if dictcnt == 0:
		flushindex(outbase, index)
	else:
		flushindex(outbase+str(dictcnt), index)

print >> sys.stderr, 'Done.'

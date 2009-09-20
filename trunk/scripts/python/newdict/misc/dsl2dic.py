#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, struct, os.path
import codecs, re

stripmark = re.compile(r'(?<!\\)\[.*?(?<!\\)\]')
def dslconv(value):
	value = stripmark.sub('', value).replace(r'\[', '[').replace(r'\]', ']')
	value = value.replace(u'\t', u'\u3000')
	return value.encode('utf-8')
dslconvkey = dslconv

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s dslfile" % (sys.argv[0])
	print "Build stardict dictionary out of Lingvo DSL source"
	sys.exit(0)
fname = sys.argv[1]
print >> sys.stderr, 'Reading...'
f = codecs.open(fname, 'r', encoding='utf-16le')
lastword = mean = None
bookname = None
lines = []
for line in f:
	if not line or line[0] in (u'\ufeff', u'#'):
		if line.find('#NAME') >= 0:
			bookname = line[line.index('#NAME')+5:].strip()
			if bookname[0] == bookname[-1] == '"':
				bookname = bookname[1:-1]
			bookname = bookname.encode('utf-8')
		continue
	if line[0] != u'\t':
		if lastword:
			try:
				assert mean
			except:
				print >> sys.stderr, lastword.encode('gbk', 
						'replace')
				raise
			lines.append((lastword, u''.join(mean)))
		lastword = line.strip()
		mean = []
	else:
		assert lastword is not None
		mean.append(line)
if lastword:
	assert mean
	lines.append((lastword, u''.join(mean)))
f.close()

print >> sys.stderr, 'Parsing...'
means = []
index = []
synlist = []
for word, mean in lines:
	if mean[-1] == '\n':
		mean = mean[:-1]
	word = dslconvkey(word)
	try:
		mean = dslconv(mean)
	except:
		print >> sys.stderr, mean
		raise
	if word.find('|') < 0:
		index.append(word)
		means.append(mean)
	else:
		ar = word.split('|')
		index.append(ar[0])
		means.append(mean)
		for s in ar[1:]:
			synlist.append([s.lower(), s, len(index)-1])
assert len(index) == len(means) == len(lines)
synlist.sort()

outbase = os.path.splitext(fname)[0]
ifofile = open(outbase + '.ifo', 'wb')
idxfile = open(outbase + '.idx', 'wb')
dicfile = open(outbase + '.dict', 'wb')

print >> sys.stderr, 'Writing data...'
sortedindex = []
for i in range(len(index)):
	offset_old = dicfile.tell()
	dicfile.write(means[i])
	sortedindex.append([index[i].lower(), index[i], i, 
		offset_old, len(means[i])])

print >> sys.stderr, 'Writing index...'
sortedindex.sort()
indexmap = {}
for i in range(len(sortedindex)):
	item = sortedindex[i]
	indexmap[item[2]] = i
	idxfile.write(item[1])
	idxfile.write('\0')
	idxfile.write(struct.pack('>LL', item[3], item[4]))

if len(synlist) > 0:
	print >> sys.stderr, 'Writing synonym...'
	synfile = open(outbase + '.syn', 'wb')
	for dummy, syn, idx in synlist:
		synfile.write(syn)
		synfile.write('\0')
		synfile.write(struct.pack('>L', indexmap[idx]))

bookname = bookname or outbase
typeseq = 'm'

if len(synlist) > 0:
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nsynwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(index), len(synlist), idxfile.tell(), bookname, typeseq))
else:
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(index), idxfile.tell(), bookname, typeseq))

ifofile.close()
idxfile.close()
dicfile.close()
if len(synlist) > 0: synfile.close()

print >> sys.stderr, 'Done.'

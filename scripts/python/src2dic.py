#!/usr/bin/env python
import sys, string, struct, os.path

assert __name__ == '__main__'

if len(sys.argv) not in (2, 3):
	print "Usage: %s [-S] tabfile" % (sys.argv[0])
	print "Build stardict dictionary from tabfile with synonym"
	print "Add -S to disable synonym"
	sys.exit(0)
if len(sys.argv) == 3:
	assert sys.argv[1] == '-S'
	withsyn = False
	fname = sys.argv[2]
else:
	withsyn = True
	fname = sys.argv[1]
outbase = os.path.splitext(fname)[0]

f = open(fname, 'r')
dicfile = open(outbase + '.dict', 'wb')
print >> sys.stderr, 'Writing data...'
index = []
for line in f:
	word, mean = line.split('\t', 1)
	if mean[-1] == '\n':
		mean = mean[:-1]
	mean = mean.replace('\\n', '\n').replace('\\\n', '\\n')
	offset_old = dicfile.tell()
	dicfile.write(mean)
	if withsyn:
		ar = word.split('|')
	else:
		ar = [word]
	index.append((ar[0].lower(), ar[0], offset_old, len(mean), ar[1:]))
f.close()

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

dicfile.close()
idxfile.close()
ifofile.close()
if len(synlist) > 0: synfile.close()

print >> sys.stderr, 'Done.'

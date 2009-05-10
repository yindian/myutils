#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, struct, os.path

def swjzconv(value):
	value = value.replace('[', '<big><font color="blue">').replace(']', '</font></big>')
	value = value.splitlines()
	if value[0].startswith('img'):
		value[0] = '<img src="%s.png">' % value[0][4:]
	value = '<br>'.join(value)
	return value

assert __name__ == '__main__'

if len(sys.argv) not in (2, 3):
	print "Usage: %s [-s] tabfile" % (sys.argv[0])
	print "Build stardict dictionary with swjz syntax"
	sys.exit(0)
if len(sys.argv) == 3:
	assert sys.argv[1].lower() == '-s'
	swjzsyntax = True
	fname = sys.argv[2]
else:
	swjzsyntax = False
	fname = sys.argv[1]
f = open(fname, 'r')
lines = f.readlines()
f.close()
lines.sort()
lines = [line.split('\t', 1) for line in lines]

means = []
index = []
synlist = []
for word, mean in lines:
	if mean[-1] == '\n':
		mean = mean[:-1]
	mean = mean.replace('\\n', '\n')
	if swjzsyntax:
		mean = swjzconv(mean)
	if word.find('|') < 0:
		index.append(word)
		means.append(mean)
	else:
		ar = word.split('|')
		index.append(ar[0])
		means.append(mean)
		for s in ar[1:]:
			synlist.append((s, len(index)-1))
assert len(index) == len(means) == len(lines)
synlist.sort()

outbase = os.path.splitext(fname)[0]
ifofile = open(outbase + '.ifo', 'wb')
idxfile = open(outbase + '.idx', 'wb')
dicfile = open(outbase + '.dict', 'wb')

for i in range(len(index)):
	offset_old = dicfile.tell()
	dicfile.write(means[i])
	idxfile.write(index[i])
	idxfile.write('\0')
	idxfile.write(struct.pack('>LL', offset_old, len(means[i])))

if len(synlist) > 0:
	synfile = open(outbase + '.syn', 'wb')
	for syn, idx in synlist:
		synfile.write(syn)
		synfile.write('\0')
		synfile.write(struct.pack('>L', idx))

if swjzsyntax:
	bookname = '段注說文解字'
	typeseq = 'h'
else:
	bookname = outbase
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

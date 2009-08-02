import sys, os.path, struct
assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s sourcefile" % (os.path.basename(sys.argv[0]))
	print "Specilized for CC-CEDICT"
	sys.exit(0)

result = []
f = open(sys.argv[1], 'r')
for line in f:
	if line.startswith('#'): continue
	line = line.split('/')
	assert line[-1] in ('\n', '')
	if line[0].find('[') > 0:
		p = line[0].find('[')
		q = line[0].index(']')
		assert q == len(line[0].strip())-1
		words = line[0][:p].strip().split()
		pron = line[0][p+1:q]
	else:
		words = line[0].strip().split()
		pron = None
	s = set()
	word = [x for x in words if x not in s and not s.add(x)]
	result.append((word, pron, line[1:-1]))
f.close()

outbase = os.path.splitext(sys.argv[1])[0]
ifofile = open(outbase + '.ifo', 'wb')
idxfile = open(outbase + '.idx', 'wb')
dicfile = open(outbase + '.dict', 'wb')
idxlist = []
synlist = []

for word, pron, mean in result:
	oldoffset = dicfile.tell()
	meanstr = '\n'.join(mean)
	dicfile.write(pron)
	dicfile.write('\0')
	dicfile.write(meanstr)
	length = len(pron) + 1 + len(meanstr)
	idxlist.append((word[0], oldoffset, length, word[1:]))

idxlist.sort()
for (word, oldoffset, length, syns), index in zip(idxlist, xrange(sys.maxint)):
	idxfile.write(word)
	idxfile.write('\0')
	idxfile.write(struct.pack('>LL', oldoffset, length))
	for syn in syns:
		synlist.append((syn, index)) # 0-based

if len(synlist) > 0:
	synlist.sort()
	synfile = open(outbase + '.syn', 'wb')
	for syn, idx in synlist:
		synfile.write(syn)
		synfile.write('\0')
		synfile.write(struct.pack('>L', idx))

bookname = 'CC-CEDICT'
typeseq = 'ym'

if len(synlist) > 0:
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nsynwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(result), len(synlist), idxfile.tell(), bookname, typeseq))
else:
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=%s\n" % (len(result), idxfile.tell(), bookname, typeseq))

ifofile.close()
idxfile.close()
dicfile.close()
if len(synlist) > 0: synfile.close()

print >> sys.stderr, 'Done.'

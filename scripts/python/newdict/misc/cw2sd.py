#!/usr/bin/env python
import sys, os.path, struct, re

def recode(str):
	return str.decode('utf-16le').encode('utf-8')

assert __name__ == '__main__'

if len(sys.argv) < 6:
	print 'Usage: %s key_list key_data word_data id_list dic_data' % (
			os.path.basename(sys.argv[0]),)
	sys.exit(0)

keypos = []
wordpos = []
idpos = []
f = open(sys.argv[1], 'rb')
while True:
	s = f.read(4)
	if not s: break
	keypos.extend(struct.unpack('<L', s))
	s = f.read(4)
	wordpos.extend(struct.unpack('<L', s))
	s = f.read(4)
	idpos.extend(struct.unpack('<L', s))
f.close()

f = open(sys.argv[2], 'rb')
keybuf = f.read()
f.close()
f = open(sys.argv[3], 'rb')
wordbuf = f.read()
f.close()

idlist = []
f = open(sys.argv[4], 'rb')
while True:
	s = f.read(8)
	if not s: break
	idlist.append(struct.unpack('<LL', s))
f.close()

indices = {}
for i in xrange(len(keypos) - 1):
	#print '%s\t%s\t%d,%d' % (recode(wordbuf[wordpos[i]:wordpos[i+1]]),
	#		recode(keybuf[keypos[i]:keypos[i+1]]),
	#		idlist[idpos[i]][0], idlist[idpos[i]][1])
	ofs = idlist[idpos[i]][1] & 0x7FFFFFFF
	if not indices.has_key(ofs):
		indices[ofs] = []
	indices[ofs].append(recode(keybuf[keypos[i]:keypos[i+1]]))

dicpos = indices.keys()
dicpos.append(idlist[-1][1])
dicpos.sort()
assert dicpos[0] == 0

for i in xrange(len(dicpos) - 1):
	syn = indices[dicpos[i]]
	for j in xrange(len(syn)):
		if not syn[j][0].isalnum():
			break
	indices[dicpos[i]] = syn[j:] + syn[:j]

appidpat = re.compile(r'"app:ID([0-9]*)"')
id2entry = lambda m: m.group(1) and ('"bword://%s"' % (indices[idlist[int(
	m.group(1))][1] & 0x7FFFFFFF][0])) or m.group(0)

f = open(sys.argv[5], 'rb')
for i in xrange(len(dicpos) - 1):
	s = f.read(dicpos[i+1] - dicpos[i])
	s = recode(s)
	s = appidpat.sub(id2entry, s)
	sys.stdout.write('%s\t%s' % ('|'.join(indices[dicpos[i]]), s))
assert f.tell() == dicpos[-1]
f.close()

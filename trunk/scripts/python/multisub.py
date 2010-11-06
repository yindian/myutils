#!/usr/bin/env python
import sys, os.path
import getopt, glob, fileinput

assert __name__ == '__main__'

opt, argv = getopt.getopt(sys.argv, 'd:h?')
opt = dict(opt)
if opt.has_key('-h') or opt.has_key('-?') or len(argv) < 2:
	print 'Linewise multiple string replacement filter'
	print 'Usage: %s [-d delimiter] pattern_file src_file(s)' % (
			os.path.basename(argv[0]),)
	print 'Each line in pattern_file is a from-to pair, delimited by -> by default'
	sys.exit(0)

delimiter = opt.get('-d', '->')

pats = []
f = open(argv[1], 'r')
for line in f:
	if line.endswith('\n'):
		line = line[:-1]
	pats.append(line.split(delimiter, 1))
	if len(pats[-1]) != 2:
		print >> sys.stderr, 'ignoring pattern not paired:', line
		del pats[-1]
	if len(pats[-1][0]) == 0:
		print >> sys.stderr, 'ignoring empty pattern:', line
		del pats[-1]
f.close()

if len(pats) == 0:
	print >> sys.stderr, 'No pattern defined.'
	sys.exit(0)

prefix = pats[0][0]
minlen = sys.maxint
maxlen = 0
for i in xrange(1, len(pats)):
	pat = pats[i][0]
	minlen = min(minlen, len(pat))
	maxlen = max(maxlen, len(pat))
	l = min(len(prefix), len(pat))
	for j in xrange(l):
		if prefix[j] != pat[j]:
			break
	if j < l and prefix[j] != pat[j]:
		prefix = prefix[:j]
	else:
		prefix = prefix[:l]

if prefix and (maxlen - minlen) < 16:
	# use hash
	pfxlen = len(prefix)
	minlen -= pfxlen
	maxlen -= pfxlen
	d = {}
	for src, dst in pats:
		d[src[pfxlen:]] = dst
	flist = []
	for fname in argv[2:]:
		flist.extend(glob.glob(fname))
	if len(flist) == 0:
		flist.append('-')
	outf = sys.stdout
	for line in fileinput.input(flist):
		ar = line.split(prefix)
		result = [ar[0]]
		for i in xrange(1, len(ar)):
			if len(ar[i]) < minlen:
				result.append(prefix)
				result.append(ar[i])
				continue
			matched = False
			for j in xrange(minlen, maxlen+1):
				if d.has_key(ar[i][:j]):
					matched = True
					break
			if not matched:
				result.append(prefix)
				result.append(ar[i])
			else:
				result.append(d[ar[i][:j]])
				result.append(ar[i][j:])
		outf.writelines(result)
else:
	# use trie
	print >> sys.stderr, 'Trie method not yet implemented.'
	sys.exit(1)

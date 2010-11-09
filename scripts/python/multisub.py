#!/usr/bin/env python
import sys, os.path
import getopt, glob, fileinput
import types, time

def trieaddstr(root, text, nodeinfo=''):
	assert type(root) == types.DictType
	assert type(text) == type(nodeinfo) == types.StringType
	if not text:
		return
	node = root
	for c in text:
		if not node.has_key(c):
			node[c] = {}
		node = node[c]
	node[None] = nodeinfo

	

assert __name__ == '__main__'

opt, argv = getopt.getopt(sys.argv[1:], 'd:h?v')
opt = dict(opt)
if opt.has_key('-h') or opt.has_key('-?') or len(argv) < 1:
	print 'Linewise multiple string replacement filter'
	print 'Usage: %s [-d delimiter] pattern_file src_file(s)' % (
			os.path.basename(sys.argv[0]),)
	print 'Each line in pattern_file is a from-to pair, delimited by -> by default'
	sys.exit(0)

delimiter = opt.get('-d', '->')
verbose = opt.has_key('-v')

pats = []
f = open(argv[0], 'r')
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

flist = []
for fname in argv[1:]:
	flist.extend(glob.glob(fname))
if len(flist) == 0:
	flist.append('-')
outf = sys.stdout

starttime = time.clock()

if prefix and (maxlen - minlen) < 16 and sum(map(lambda a: a[0].count(prefix),
	pats)) == len(pats): # split can't handle multiple occurrence of prefix
	if verbose:
		print >> sys.stderr, 'Using hash.'
	# use hash
	pfxlen = len(prefix)
	minlen -= pfxlen
	maxlen -= pfxlen
	d = {}
	for src, dst in pats:
		d[src[pfxlen:]] = dst
	bytes = 0
	lineno = 0
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
		lineno += 1
		bytes += len(line)
		if verbose and lineno % 10000 == 0:
			print >> sys.stderr, '\rBytes per second:', bytes / (time.clock() - starttime),
else:
	if verbose:
		print >> sys.stderr, 'Using trie.'
	# use trie
	trie = {}
	for src, dst in pats:
		trieaddstr(trie, src, dst)
	bytes = 0
	lineno = 0
	for line in fileinput.input(flist):
		result = []
		linelen = len(line)
		i = 0 # current cursor
		j = -1 # cursor at trie root entry
		node = trie # current trie node, starting at root
		while i < linelen:
			c = line[i]
			if node.has_key(c):
				if j < 0:
					j = i
				i += 1
				node = node[c]
				if node.has_key(None): # has pattern
					result.append(node[None]) # replace
					node = trie # rewind to trie root
					j = -1
			elif j < 0:
				i += 1
				result.append(c)
			else:
				i = j+1 # starting at j has no pattern
				result.append(line[j])
				node = trie # rewind to trie root
				j = -1
		if j >= 0: # unfinished match
			result.append(line[j:])
		outf.writelines(result)
		lineno += 1
		bytes += linelen
		if verbose and lineno % 10000 == 0:
			print >> sys.stderr, '\rBytes per second:', bytes / (time.clock() - starttime),

endtime = time.clock()
if verbose:
	print >> sys.stderr, '\nElapsed time: %.2f seconds'% (endtime - starttime)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

separator = ' '

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print "Usage: %s filename" % (sys.argv[0])
	print "Resolve synonym for foldoc dict file"
	sys.exit(0)

syndb = {}
f = open(sys.argv[1], 'r')
for line in f:
	if not line.startswith('\t') and not line.startswith(' '*8):
		ar = line[:-1].split(separator)
		if len(ar) == 1:
			continue
		for word in ar[1:]:
			if not syndb.has_key(word):
				syndb[word] = set([])
			if ar[0] not in syndb[word]:
				syndb[word].add(ar[0])
f.close()
keys = syndb.keys()
keys.sort()
for word in keys:
	sys.stdout.write(word)
	sys.stdout.write('\n\t'.join(['']+['{%s}' % (s) for s in syndb[word]]))
	sys.stdout.write('\n')

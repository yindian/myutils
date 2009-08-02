#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string

assert __name__ == '__main__'

if len(sys.argv) != 3:
	print 'Usage: %s tabfile wordlist' % (os.path.basename(sys.argv[0]),)
	print 'tabfile and wordlist shall have the same number of lines'
	sys.exit(0)

f = open(sys.argv[1], 'r')
lines = f.readlines()
f.close()
f = open(sys.argv[2], 'r')
words = f.readlines()
f.close()
assert len(lines) == len(words)

for line, syn in zip(lines, words):
	assert line[-1] == syn[-1] == '\n'
	word, mean = line[:-1].split('\t', 1)
	syn = syn[:-1]
	#s = set(word.split('|')).union(set(syn.split('|')))
	assert word.find('|') < 0 and syn.find('|') < 0
	if word != syn:
		word = '%s|%s' % (word, syn)
		#word = '%s|%s(%s)' % (word, syn, word)
	sys.stdout.write(word)
	sys.stdout.write('\t')
	sys.stdout.write(mean)
	sys.stdout.write('\n')

#!/usr/bin/env python
import sys, os.path

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s tabfile.txt' % (os.path.basename(sys.argv[0]),)
	print r'Will substitute "^\([^\t|]*\)\([^\t]*\)\t\(.*\)\n\1|\([^\t]*\)\t\3$" to "\1\2\4\t\3"'
	sys.exit(0)

lastword = lastmean = None
f = open(sys.argv[1], 'r')
for line in f:
	word, mean = line.rstrip('\r\n').split('\t', 1)
	word = word.split('|')
	if lastword and lastword[0] == word[0] and lastmean == mean:
		lastword.extend(word[1:])
	else:
		if lastword:
			print '%s\t%s' % ('|'.join(lastword), lastmean)
		lastword = word
		lastmean = mean
f.close()
if lastword:
	print '%s\t%s' % ('|'.join(lastword), lastmean)

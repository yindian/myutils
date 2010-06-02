#!/usr/bin/env python
import sys, os.path
from viqrtelexuniconv import uni2viqr

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s tabfile" % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'r')
for line in f:
	ar = line.split('\t', 1)
	if len(ar) < 2:
		sys.stdout.write(line)
		continue
	sys.stdout.write(uni2viqr(ar[0].decode('utf-8')).encode('utf-8'))
	sys.stdout.write('\t')
	sys.stdout.write(ar[1])
f.close()

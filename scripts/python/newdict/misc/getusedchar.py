#!/usr/bin/env python
import sys
assert __name__ == '__main__'
used = set()
for line in sys.stdin:
	line = line.decode('utf-8').rstrip()
	for c in line:
		used.add(c)
for c in sorted(list(used)):
	print '%s\tU+%04X' % (c.encode('utf-8'), ord(c))

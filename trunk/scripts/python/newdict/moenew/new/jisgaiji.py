#!/usr/bin/env python
import sys, os.path

assert __name__ == '__main__'

gaiji = []

for line in sys.stdin:
	line = line.decode('utf-8')
	for c in line:
		try:
			c.encode('euc-jp')
		except:
			if 0xDC00 <= ord(c) < 0xE000:
				gaiji[-1] += c
			else:
				gaiji.append(c)

gaiji.sort()
result = [gaiji[0]]
for c in gaiji:
	if c != result[-1]:
		result.append(c)

for c in result:
	print c.encode('utf-8')

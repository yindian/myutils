#!/usr/bin/env python
import sys, os.path, re

assert __name__ == '__main__'

if len(sys.argv) != 3:
	print 'Usage: %s GaijiMap.xml alternate.ini' % (
			os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[2], 'r')
altmap = {}
for line in f:
	line = line.strip()
	if not line.startswith('u'):
		continue
	ar = line.split()
	assert len(ar) >= 2
	code = int(ar[0][1:], 16)
	altmap[code] = ar[1]
f.close()

unipat = re.compile(r'''unicode *= *["']#([^"']*)["']''')
f = open(sys.argv[1], 'r')
for line in f:
	if line.startswith('<gaijiMap') and line.find('alt') < 0:
		ar = unipat.findall(line)
		assert len(ar) == 1
		code = ar[0]
		if code[0].lower() == 'x':
			code = int(code[1:], 16)
		else:
			code = int(code, 0)
		if altmap.has_key(code):
			p = line.rfind('/>')
			assert p > 0
			line = line[:p] + ' alt="%s"'%(altmap[code],) + line[p:]
	sys.stdout.write(line)
f.close()

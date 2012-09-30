#!/usr/bin/env python
import sys
import re
bracepat = re.compile(r'\\\w+{([^{}]*)}', re.S)
idx = int(sys.argv[1])
en = open('omao%02d.txt' % (idx,)).readlines()
zh = open('y%02d.txt' % (idx,)).readlines()

assert en[0].startswith('\\section')
assert zh[0].startswith('\\section')

print bracepat.findall(zh[0])[0]
print bracepat.findall(en[0])[0]

i = j = 1
zhl = len(zh)
enl = len(en)
while True:
	while i < zhl and not zh[i].startswith('\\qitem'):
		i += 1
	while j < enl and not en[j].startswith('\\qitem'):
		j += 1
	i += 1
	j += 1
	print
	buf = []
	while i < zhl and not zh[i].startswith('\\endqitem'):
		if not zh[i].startswith('%') and not zh[i].startswith('\\midqitem'):
			buf.append(zh[i].rstrip())
		i += 1
	print bracepat.sub(r'\g<1>', '\n'.join(buf))
	print
	buf = []
	while j < enl and not en[j].startswith('\\endqitem'):
		if not en[j].startswith('%') and not en[j].startswith('\\midqitem'):
			buf.append(en[j].rstrip())
		j += 1
	print bracepat.sub(r'\g<1>', '\n'.join(buf))
	if i > zhl and j > enl:
		break

print
print

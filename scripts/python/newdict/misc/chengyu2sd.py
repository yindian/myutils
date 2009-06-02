#!/usr/bin/env python
import sys, glob, re

assert __name__ == '__main__'

deltag = re.compile(r'<.*?>', re.S)

flist = glob.glob('*/*/*.yhl')
num = len(flist)
now = 0
cnt = 0
step = num / 20

for fname in flist:
	if cnt == 0:
		print >> sys.stderr, 'Processing... (%d/%d)' % (now, num)
	now += 1
	cnt += 1
	if cnt == step: cnt = 0
	f = open(fname, 'r')
	buf = f.read()
	f.close()
	p = buf.index('<title>') + len('<title>')
	q = buf.index('</title>')
	word = buf[p:q].strip()
	mean = deltag.sub('', buf[q:]).strip()
	sys.stdout.write(word)
	sys.stdout.write('\t')
	sys.stdout.write(mean.replace('\n', '\\n'))
	sys.stdout.write('\n')
print >> sys.stderr, 'Done. (%d/%d)' % (now, num)

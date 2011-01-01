#!/usr/bin/env python
import sys, os.path

def splitheadbody(mbsrc):
	if mbsrc.startswith(u'\ufeff'):
		mbsrc = mbsrc[1:]
	p = mbsrc.find('[Text]')
	if p >= 0:
		p = mbsrc.index('\n', p) + 1
		return mbsrc[:p], mbsrc[p:]
	return u'', mbsrc

isuro = lambda c: 0x4E00 <= ord(c) <= 0x9FA5
firsthanzi = lambda s: s[0] in '~^!' and s[1] or s[0]

assert __name__ == '__main__'

if len(sys.argv) < 4:
	print 'Usage: %s first_mb_src second_mb_src output_mb_src' % (
			os.path.basename(sys.argv[0]),)
	print 'Merge two MB source files. Items in first precede second.'
	print 'The lines before [Text] are maintained.'
	print 'Input & output files are in UTF-16LE encoding with BOM. CR LF.'
	print 'If first_mb_src is specified as -s, then only output single char entries in second_mb_src, one entry a line.'
	sys.exit(0)

if sys.argv[1] == '-s':
	f = open(sys.argv[2], 'rb')
	mb = f.read().decode('utf-16le')
	f.close()
	head, body = splitheadbody(mb)
	result = {}
	for line in body.splitlines():
		ar = line.rstrip().split()
		if not ar:
			continue
		if ar[0].startswith('`'):
			ar[0] = ar[0][1:]
		assert ar[0]
		if not result.has_key(ar[0]):
			result[ar[0]] = []
		for s in ar[1:]:
			if s[0] in '~^!':
				s = s[1:]
			if len(s) > 1 and not (0xD800 <= ord(s[0]) < 0xDC00 and
					len(s) == 2):
				continue
			if s not in result[ar[0]]:
				result[ar[0]].append(s)
	f = open(sys.argv[3], 'wb')
	f.write(u'\ufeff'.encode('utf-16le'))
	for k in sorted(result.iterkeys()):
		if not result[k]:
			continue
		for s in result[k]:
			f.write(('%s %s\r\n' % (k, s)).encode('utf-16le'))
	f.close()
	sys.exit(0)

f = open(sys.argv[1], 'rb')
firstmb = f.read().decode('utf-16le')
f.close()
f = open(sys.argv[2], 'rb')
secondmb = f.read().decode('utf-16le')
f.close()

firsthead, firstbody = splitheadbody(firstmb)
secondhead, secondbody = splitheadbody(secondmb)

result = {}
for line in firstbody.splitlines() + secondbody.splitlines():
	ar = line.rstrip().split()
	if not ar:
		continue
	if ar[0].startswith('`'):
		ar[0] = ar[0][1:]
	assert ar[0]
	if not result.has_key(ar[0]):
		result[ar[0]] = []
	for s in ar[1:]:
		if s not in result[ar[0]]:
			result[ar[0]].append(s)

for k in sorted(result.iterkeys()): # rearrange order to make hanzi first
	for p in xrange(len(result[k])):
		if isuro(firsthanzi(result[k][p])):
			break
	if p > 0 and p < len(result[k]) and isuro(result[k][p][0]):
		result[k] = [result[k][p]] + result[k][:p] + result[k][p+1:]

f = open(sys.argv[3], 'wb')
f.write(u'\ufeff'.encode('utf-16le'))
f.write((firsthead or secondhead).encode('utf-16le'))
for k in sorted(result.iterkeys()):
	assert result[k]
	f.write(('%s %s\r\n' % (k, ' '.join(result[k]))).encode('utf-16le'))
f.close()

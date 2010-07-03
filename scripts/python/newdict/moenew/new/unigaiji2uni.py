#!/usr/bin/env python
import sys, os.path

def fwhex(code):
	result = []
	for c in '%04X' % (code,):
		result.append(unichr(ord(c) + 0xfee0))
	return u''.join(result)

def ismatch(code):
	return 0x4E00 <= code <= 0x9FA5

assert __name__ == '__main__'

codeset = set()

for line in sys.stdin:
	ar = line.split('&#')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s[0] == 'x':
			code = int(s[1:p], 16)
		else:
			code = int(s[:p])
		if ismatch(code):
			result.append('&#xFFF0;')
			result.append(fwhex(code).encode('sjis'))
			result.append('&#xFFF1;')
			codeset.add(code)
		else:
			result.append('&#')
			result.append(s[:p+1])
		result.append(s[p+1:])
	sys.stdout.write(''.join(result))

for code in sorted(list(codeset)):
	print >> sys.stderr, 'u%04X\t%04X' % (code, code)

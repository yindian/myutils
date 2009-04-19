#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

for line in sys.stdin:
	line = unicode(line, 'utf-8')
	result = []
	for c in line:
		result.append(c)
		if 0xD800 <= ord(c) <= 0xDBFF:
			last = c
		elif 0xDC00 <= ord(c) <= 0xDFFF:
			code0 = ord(last)
			code1 = ord(c)
			codePoint = ((code0 - 0xD800) << 10) + (
					(code1 - 0xDC00)) + 0x10000
			result.append('(U+%X)' % codePoint)
	sys.stdout.write(''.join(result).encode('utf-8'))

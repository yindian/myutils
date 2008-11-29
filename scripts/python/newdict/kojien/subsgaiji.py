#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

def char2utf8(code):
	if code < 0x10000:
		return unichr(code).encode('utf-8')
	else:
		assert code < 0x200000
		return ''.join(map(chr, [
			0xf0 | (code >> 18),
			0x80 | ((code >> 12) & 0x3f),
			0x80 | ((code >> 6) & 0x3f),
			0x80 | (code & 0x3f)]))

def touni(str):
	if not str or str[0].lower() != 'u':
		return ''
	return ''.join(map(lambda s: char2utf8(int(s[1:], 16)), str.split(',')))

fileenc = 'utf-8'

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: %s filename gaijimap" % (sys.argv[0])
		print "This version is specialized for Kojien"
		sys.exit(0)
	f = open(sys.argv[2], 'r')
	narrow = {}
	wide = {}
	for line in f:
		if line.startswith('#') or len(line) < 2:
			continue
		assert line[0] in 'hz'
		line = line.split('\t')
		code = line[0][1:].lower()
		if line[1]:
			what = (touni(line[1]),)
		elif line[2]:
			what = (line[2],)
		elif len(line) > 4:
			what = (None, unicode(' '.join(line[4:]), fileenc
				).encode('utf-8'))
		else:
			what = (None, '')
		if line[0][0] == 'h':
			narrow[code] = what
		else:
			wide[code] = what
	f.close()
	f = open(sys.argv[1], 'r')
	for line in f:
		pos = line.find('<?')
		while pos >= 0:
			assert line[pos+2] in 'nw'
			assert line[pos+8] == '>'
			if line[pos+2] == 'n':
				dic = narrow
			else:
				dic = wide
			sub = dic.setdefault(line[pos+4:pos+8],
					('{'+line[pos+1:pos+8]+'}',))
			if len(sub) == 1:
				pass
			elif sub[1]:
				dic[line[pos+4:pos+8]] = sub = ('{'+
						line[pos+1:pos+8]+', %s}'
						% (sub[1]),)
			else:
				dic[line[pos+4:pos+8]] = sub = ('{'+
						line[pos+1:pos+8]+'}',)
			line = line.replace(line[pos:pos+9], sub[0])
			pos = line.find('<?')
		sys.stdout.write(line)
	f.close()

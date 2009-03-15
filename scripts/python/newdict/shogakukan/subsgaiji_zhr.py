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
		return str
	return ''.join(map(lambda s: char2utf8(int(s[1:], 16)), str.split(',')))

def ansi2uni(line, fileenc):
	line = line.split('<?')
	result = []
	result.append(unicode(line[0], fileenc).encode('utf-8'))
	for s in line[1:]:
		assert s[0] in 'nwgc/'
		result.append('<?')
		if s[0] in 'nwg':
			pos = s.find('>')
			result.append(s[:pos+1])
			result.append(unicode(s[pos+1:], 
				fileenc).encode('utf-8'))
		elif s[0] == 'c':
			result.append(s)
		else:
			result.append(unicode(s, fileenc).encode('utf-8'))
	return ''.join(result)

fileenc = 'euc-jp'
gaijifileenc = 'utf-8'
gbenc = 'gb2312'

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: %s filename gaijimap" % (sys.argv[0])
		print "This version is specialized for Shogakukan Zhongri"
		sys.exit(0)
	f = open(sys.argv[2], 'r')
	alldic = {}
	alldic['h'] = alldic['n'] = {}
	alldic['z'] = alldic['w'] = {}
	alldic['g'] = {}
	alldic['c'] = {}
	for line in f:
		if line.startswith('#') or len(line) < 2:
			continue
		assert line[0] in 'hzgc'
		line = line[:-1].split('\t')
		code = line[0][1:].lower()
		if line[1] and line[1] != '-':
			if line[1].lower() == 'null':
				what = ('',)
			else:
				what = (touni(line[1]),)
		elif len(line) > 2 and line[2] and line[2] != '-':
			what = (line[2],)
		elif len(line) > 4:
			what = (None, unicode(' '.join(line[4:]), gaijifileenc
				).encode('utf-8'))
		else:
			what = (None, '')
			#print >> sys.stderr, 'Cannot substitute', line
			#what = ('',)
		alldic[line[0][0]][code] = what
	f.close()
	f = open(sys.argv[1], 'r')
	for line in f:
		line = ansi2uni(line, fileenc)
		pos = line.find('<?')
		while pos >= 0:
			#assert line[pos+2] in 'nw'
			#assert line[pos+8] == '>'
			if (line[pos+2] in 'nw' and line[pos+8] == '>'):
				dic = alldic[line[pos+2]]
				sub = dic.setdefault(line[pos+4:pos+8],
						('{'+line[pos+1:pos+8]+'}',))
				if len(sub) == 1:
					pass
				elif sub[1]:
					dic[line[pos+4:pos+8]] = sub = ('{'+
							line[pos+1:pos+8]+',%s}'
							% (sub[1]),)
				else:
					dic[line[pos+4:pos+8]] = sub = ('{'+
							line[pos+1:pos+8]+'}',)
				line = line.replace(line[pos:pos+9], sub[0])
			elif (line[pos+2] == 'g' and line[pos+11] == '>'):
				dic = alldic[line[pos+2]]
				gbchar = line[pos+9:pos+11]
				if ord(gbchar[0]) >= 0xB0 or not dic.has_key(
						line[pos+4:pos+8]):
					sub = unicode(gbchar, gbenc)
					sub = (sub.encode('utf-8'),)
				else:
					sub = dic.setdefault(line[pos+4:pos+8],
						('{'+line[pos+1:pos+8]+'}',))
				if len(sub) == 1:
					pass
				elif sub[1]:
					dic[line[pos+4:pos+8]] = sub = ('{'+
							line[pos+1:pos+8]+',%s}'
							% (sub[1]),)
				else:
					dic[line[pos+4:pos+8]] = sub = ('{'+
							line[pos+1:pos+8]+'}',)
				line = line.replace(line[pos:pos+12], sub[0])
			elif (line[pos+2:pos+4] == 'c>'):
				dic = alldic[line[pos+2]]
				npos = pos+4
				subs = []
				while line[npos] != '<':
					code = (ord(line[npos]) - 0x80)
					code = (code << 8 ) | (ord(
						line[npos+1]) - 0x80)
					code = '%04x' % (code)
					sub = dic.setdefault(code,
						('{?c='+code+'}',))
					if len(sub) == 1:
						pass
					elif sub[1]:
						dic[code] = sub = ('{?c='+
								code+',%s}'
								% (sub[1]),)
					else:
						dic[code] = sub = ('{?c='+
								code+'}',)
					subs.append(sub[0])
					npos += 2
				assert line[npos:npos+5] == '<?/c>'
				subs = ''.join(subs)
				line = line.replace(line[pos:npos+5], subs)
			else:
				raise
			pos = line.find('<?')
		sys.stdout.write(line)
	f.close()

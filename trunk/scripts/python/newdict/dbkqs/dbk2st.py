#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path

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

def iscjk(c):
	p = ord(c)
	if 0x4e00 <= p <= 0x9fc3 or 0x3400 <= p <= 0x4db5 or\
		0xf900 <= p <= 0xfad9 or 0x20000 <= p <= 0x2a6d6 or\
		0x2f800 <= p <= 0x2fa1d or p == 0x3007: # CJK characters
		return True
	elif 0xD800 <= p <= 0xDFFF: # surrogate pair for narrow python
		return True
	#elif c in u'{/@}|':
	#	return True
	else:
		return False

def subsuni(str):
	ar = str.split('?u=')
	for i in range(1, len(ar)):
		if ar[i-1][-1] == '<':
			ar[i-1] = ar[i-1][:-1]
			p = ar[i].index('>')
			code = int(ar[i][:p], 16)
			ar[i] = char2utf8(code) + ar[i][p+1:]
		else:
			assert ar[i-1].rfind('{') >= 0
			p = ar[i].index('}')
			code = int(ar[i][:p], 16)
			ar[i] = '|' + char2utf8(code) + ar[i][p:]
	return ''.join(ar)

matching = {
		u'\u300a': u'\u300b',
		u'\u201c': u'\u201d',
		}

def gettitle(str):
	ar = str.split('|')
	result = []
	for s in ar:
		s = unicode(subsuni(s), 'utf-8')
		if s.find('{') >= 0: # }
			p = s.find('{')
			assert s.find('{', p+1) < 0
			assert s.find('}', 0, p) < 0
			try:
				q = s.index('}', p)
			except:
				print >> sys.stderr, p, `s`
				raise
			if s.find('|', p+1, q) < 0:
				assert iscjk(s[p+1])
				result.append(s[:p] + s[p+1:q] + s[q+1:])
			else:
				aa = s[p+1:q].split('|')
				result += [s[:p] + x + s[q+1:] for x in aa]
		else:
			assert s.find('<?') < 0
			result.append(s)
	for i in range(len(result)):
		c = result[i][0]
		if c.isalnum() or iscjk(c): continue
		cc = matching[c]
		if cc is None:# or result[i].find(cc) < 0:
			result[i] = result[i][1:]
		else:
			p = result[i].index(cc)
			result[i] = result[i][1:p] + result[i][p+1:]
	result = list(set(result))
	return '|'.join([s.encode('utf-8') for s in result])

def output(result):
	sys.stdout.write(result[0])
	sys.stdout.write('\t')
	lastempty = False
	for line in result[1:]:
		if not line.strip():
			if lastempty: continue
			lastempty = True
		else:
			lastempty = False
			sys.stdout.write(line)
		sys.stdout.write('\\n')
	sys.stdout.write('\n')

def showhelp():
	print "Usage: %s txtfile" % (os.path.basename(sys.argv[0]))
	print "Convert dai bak ka source to stardict tab file."
	sys.exit(0)

if __name__ == '__main__':
	if not len(sys.argv) == 2:
		showhelp()
	f = open(sys.argv[1], 'r')
	state = 0
	result = None
	for line in f:
		line = line[:-1]
		if line == '</>':
			state = 0
			if result:
				output(result)
				result = None
			else:
				print >> sys.stderr, 'Ignore empty line'
		elif state == 0:
			try:
				result = [gettitle(line.strip())]
				result += [subsuni(line)]
			except:
				print >> sys.stderr, 'Error getting title for',
				print >> sys.stderr, unicode(line, 'utf-8'
						).encode('gbk', 'replace')
				raise
			state = 1
		else:
			#if line.find('<br>') < 0:
			#	line = line + '<br>'
			result.append(subsuni(line))#.replace('<br>', '\\n'))
	if result:
		print ''.join(result)
	f.close()

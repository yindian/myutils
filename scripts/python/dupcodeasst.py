#!/usr/bin/env python
import sys, os.path
import pprint, pdb

def cjkclass(c):
	if not c:
		return 0
	if type(c) != type(u''):
		c = c.decode('utf-8')
	code = ord(c[0])
	if 0xD800 <= code < 0xDC00:
		if len(c) < 2 or not 0xDC00 <= ord(c[1]) < 0xE000:
			return 0
		code = 0x10000+ (((code - 0xD800) << 10) | (ord(c[1]) - 0xDC00))
	if 0x4E00 <= code <= 0x9FFF: # URO (up to 0x9FA5) or CJK Basic
		return 1
	elif 0xF900 <= code <= 0xFAFF: # CJK Compat
		return 2
	elif 0x3400 <= code <= 0x4DBF: # CJK Ext-A
		return 3
	elif 0x20000 <= code <= 0x2A6DF: # CJK Ext-B
		return 4
	elif 0x2F800 <= code <= 0x2FA1F: # CJK Compat Supplement
		return 5
	elif 0x2A700 <= code <= 0x2B73F: # CJK Ext-C
		return 6
	elif 0x2B740 <= code <= 0x2B81F: # CJK Ext-D
		return 7
	else:
		return 0

iscjk = lambda c: cjkclass(c) > 0
notids = lambda c: not 0x2FF0 <= ord(c) <= 0x2FFF

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

def loadIDS(chisepath):
	ids = {}
	fnlist = '''\
IDS-UCS-Basic.txt
IDS-UCS-Compat-Supplement.txt
IDS-UCS-Compat.txt
IDS-UCS-Ext-A.txt
IDS-UCS-Ext-B-1.txt
IDS-UCS-Ext-B-2.txt
IDS-UCS-Ext-B-3.txt
IDS-UCS-Ext-B-4.txt
IDS-UCS-Ext-B-5.txt
IDS-UCS-Ext-B-6.txt\
'''.splitlines()
	for fname in fnlist:
		f = open(os.path.join(chisepath, fname), 'r')
		lineno = 0
		try:
			for line in f:
				lineno += 1
				if line.startswith(';'):
					continue
				line = line.strip()
				if not line:
					continue
				ar = line.split('\t')
				assert len(ar) == 3 or (len(ar) == 4 and
						ar[3] == '?')
				assert ar[0][0] == 'U' and ar[0][1] in '+-'
				code = int(ar[0][2:], 16)
				assert char2utf8(code) == ar[1]
				ids[ar[1]] = ar[2].decode('utf-8')
		except:
			print >> sys.stderr, 'Error on %s:%d' % (fname, lineno)
			pass
		f.close()
	return ids

def _getids(ids, newids, word):
	if newids.has_key(word):
		return newids[word]
	if not ids.has_key(word):
		return None
	result = []
	newids[word] = None
	i = 0
	olddecomp = ids[word]
	while i < len(olddecomp):
		j = i+1
		if 0xD800 <= ord(olddecomp[i]) < 0xDC00:
			j += 2
		elif olddecomp[i] == '&':
			j = olddecomp.index(';', i) + 1
		part = olddecomp[i:j].encode('utf-8')
		partids = _getids(ids, newids, part)
		if partids is None:
			partids = olddecomp[i:j]
		result.append(partids)
		i = j
	newids[word] = ''.join(result)
	return newids[word]

def expandIDS(ids):
	newids = {}
	for word in ids.iterkeys():
		_getids(ids, newids, word)
	return newids

def getassistcodes(wordlist, word2code, ids):
	result = []
	word = refword = None
	for i in xrange(len(wordlist)):
		word = wordlist[i]
		if word not in ids:
			print >> sys.stderr, 'Missing', word
			break
		refword = wordlist[i == 0 and 1 or 0]
		if refword not in ids:
			print >> sys.stderr, 'Missing', refword
			break
		decomp = ''.join(filter(notids, ids[word]))
		refdecomp = ''.join(filter(notids, ids[refword]))
		for p in xrange(min(len(decomp), len(refdecomp))):
			if decomp[p] != refdecomp[p]:
				break
		try:
			assert decomp[p] != refdecomp[p]
		except:
			print >> sys.stderr, word, refword, p,
			print >> sys.stderr, decomp.encode('utf-8'),
			print >> sys.stderr, refdecomp.encode('utf-8')
			pass
		while p > 0 and not (iscjk(decomp[p:p+2]) or decomp[p] == '&'):
			p -= 1
		while p < len(decomp)-1 and not (iscjk(decomp[p:p+2]) or
				decomp[p] == '&'):
			p += 1
		if 0xD800 <= ord(decomp[p]) < 0xDC00:
			part = decomp[p:p+2]
		elif decomp[p] == '&':
			part = decomp[p:decomp.index(';', p)]
		else:
			part = decomp[p]
		part = part.encode('utf-8')
		result.append((word, word2code.get(part, '?')[0], part))
	return result

assert __name__ == '__main__'

if len(sys.argv) != 4:
	print 'Usage: %s mb.txt chise_path out_mb_w_asst.txt' % (
			os.path.basename(sys.argv[0]),)
	print 'mb input format: each line is space separated code & word'
	print 'All input/output files are UTF-8 encoded.'
	sys.exit(0)

print >> sys.stderr, 'Loading MB...'
code2word = {}
word2code = {}
f = open(sys.argv[1], 'r')
for line in f:
	code, word = line.strip().split()
	if not code2word.has_key(code):
		code2word[code] = []
	if word not in code2word[code]:
		code2word[code].append(word)
	if not word2code.has_key(word) or len(code) > len(word2code[word]):
		word2code[word] = code
f.close()

duplist = []
for code in sorted(code2word.iterkeys()):
	if len(code2word[code]) > 10:
		#print '%s\t%s' % (code, ' '.join(code2word[code]))
		duplist.append((code, filter(iscjk, code2word[code])))

print >> sys.stderr, 'Loading IDS...'
ids = loadIDS(sys.argv[2])
ids = expandIDS(ids)

print >> sys.stderr, 'Generating assist codes...'
f = open(sys.argv[3], 'w')
for code, wordlist in duplist:
	#if code == 'fpgc':
	#	pdb.set_trace()
	if len(code) < 4 or len(wordlist) < 2:
		continue
	assistcodes = getassistcodes(wordlist, word2code, ids)
	for word, asstcode, part in assistcodes:
		print >> f, '%s%s %s # %s' % (code, asstcode, word, part)
f.close()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unicodedata import normalize

tonemarkset = u'sfrxj'
compoundset = u'aeoudw'
tonemarksetviqr = u"'`?~."
compoundsetviqr = u'^+d('
tonetransform = {
	u'a':      u'\u00e1\u00e0\u1ea3\u00e3\u1ea1',
	u'\u0103': u'\u1eaf\u1eb1\u1eb3\u1eb5\u1eb7',
	u'\u00e2': u'\u1ea5\u1ea7\u1ea9\u1eab\u1ead',
	u'e':      u'\u00e9\u00e8\u1ebb\u1ebd\u1eb9',
	u'\u00ea': u'\u1ebf\u1ec1\u1ec3\u1ec5\u1ec7',
	u'i':      u'\u00ed\u00ec\u1ec9\u0129\u1ecb',
	u'o':      u'\u00f3\u00f2\u1ecf\u00f5\u1ecd',
	u'\u00f4': u'\u1ed1\u1ed3\u1ed5\u1ed7\u1ed9',
	u'\u01a1': u'\u1edb\u1edd\u1edf\u1ee1\u1ee3',
	u'u':      u'\u00fa\u00f9\u1ee7\u0169\u1ee5',
	u'\u01b0': u'\u1ee9\u1eeb\u1eed\u1eef\u1ef1',
	u'y':      u'\u00fd\u1ef3\u1ef7\u1ef9\u1ef5'
}
compoundtrasform = {
	u'aa': u'\u00e2',
	u'aw': u'\u0103',
	u'ee': u'\u00ea',
	u'oo': u'\u00f4',
	u'ow': u'\u01a1',
	u'uw': u'\u01b0',
	u'dd': u'\u0111'
}
compoundtrasformviqr = {
	u'a^': u'\u00e2',
	u'a(': u'\u0103',
	u'e^': u'\u00ea',
	u'o^': u'\u00f4',
	u'o+': u'\u01a1',
	u'u+': u'\u01b0',
	u'dd': u'\u0111'
}
revcompoundtrasform, revcompoundtrasformviqr = map(lambda d: dict([(v, k) for k, v in d.iteritems()]), (compoundtrasform, compoundtrasformviqr))
loweralphas = u'abcdefghijklmnopqrstuvwxyz\u00e2\u0103\u00ea\u00f4\u01a1\u01b0\u0111\u00e1\u00e0\u1ea3\u00e3\u1ea1\u1eaf\u1eb1\u1eb3\u1eb5\u1eb7\u1ea5\u1ea7\u1ea9\u1eab\u1ead\u00e9\u00e8\u1ebb\u1ebd\u1eb9\u1ebf\u1ec1\u1ec3\u1ec5\u1ec7\u00ed\u00ec\u1ec9\u0129\u1ecb\u00f3\u00f2\u1ecf\u00f5\u1ecd\u1ed1\u1ed3\u1ed5\u1ed7\u1ed9\u1edb\u1edd\u1edf\u1ee1\u1ee3\u00fa\u00f9\u1ee7\u0169\u1ee5\u1ee9\u1eeb\u1eed\u1eef\u1ef1\u00fd\u1ef3\u1ef7\u1ef9\u1ef5'
upperalphas = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ\u00c2\u0102\u00ca\u00d4\u01a0\u01af\u0110\u00c1\u00c0\u1ea2\u00c3\u1ea0\u1eae\u1eb0\u1eb2\u1eb4\u1eb6\u1ea4\u1ea6\u1ea8\u1eaa\u1eac\u00c9\u00c8\u1eba\u1ebc\u1eb8\u1ebe\u1ec0\u1ec2\u1ec4\u1ec6\u00cd\u00cc\u1ec8\u0128\u1eca\u00d3\u00d2\u1ece\u00d5\u1ecc\u1ed0\u1ed2\u1ed4\u1ed6\u1ed8\u1eda\u1edc\u1ede\u1ee0\u1ee2\u00da\u00d9\u1ee6\u0168\u1ee4\u1ee8\u1eea\u1eec\u1eee\u1ef0\u00dd\u1ef2\u1ef6\u1ef8\u1ef4'
lower2upper = dict(zip(loweralphas, upperalphas))
upper2lower = dict(zip(upperalphas, loweralphas))
def telex2uni(str):
	if len(str) <= 1:
		return str
	result = [str[0]]
	for i in range(1, len(str)):
		ch = str[i].lower()
		if ch in tonemarkset and tonetransform.has_key(result[-1].lower()):
			if tonetransform.has_key(result[-1]): # lower case
				result[-1] = tonetransform[result[-1]][tonemarkset.index(ch)]
			else: # upper case
				result[-1] = lower2upper[tonetransform[result[-1].lower()][tonemarkset.index(ch)]]
		elif ch in compoundset and compoundtrasform.has_key(result[-1].lower() + ch):
			if compoundtrasform.has_key(result[-1] + ch): # lower case
				result[-1] = compoundtrasform[result[-1] + ch]
			else:
				result[-1] = lower2upper[compoundtrasform[result[-1].lower() + ch]]
		else:
			result.append(str[i])
	return u''.join(result)
def viqr2uni(str):
	if len(str) <= 1:
		return str
	result = [str[0]]
	for i in range(1, len(str)):
		ch = str[i].lower()
		if ch in tonemarksetviqr and tonetransform.has_key(result[-1].lower()):
			if tonetransform.has_key(result[-1]): # lower case
				result[-1] = tonetransform[result[-1]][tonemarksetviqr.index(ch)]
			else: # upper case
				result[-1] = lower2upper[tonetransform[result[-1].lower()][tonemarksetviqr.index(ch)]]
		elif ch in compoundsetviqr and compoundtrasformviqr.has_key(result[-1].lower() + ch):
			if compoundtrasformviqr.has_key(result[-1] + ch): # lower case
				result[-1] = compoundtrasformviqr[result[-1] + ch]
			else:
				result[-1] = lower2upper[compoundtrasformviqr[result[-1].lower() + ch]]
		else:
			result.append(str[i])
	return u''.join(result)

def uni2telex(ustr):
	ustr = normalize('NFC', ustr)
	result = []
	for c in ustr:
		if c in upperalphas:
			uppercase = True
			c = upper2lower[c]
		elif c in loweralphas:
			uppercase = False
		else:
			if ord(c) < 0x80:
				result.append(chr(ord(c)))
			else:
				result.append(c)
			continue
		base = c
		toneidx = -1
		for k, v in tonetransform.iteritems():
			if c in v:
				base = k
				toneidx = v.index(c)
				break
		if revcompoundtrasform.has_key(base):
			s = revcompoundtrasform[base].encode('ascii')
			if uppercase:
				result.append(lower2upper[s[0]] + s[1:])
			else:
				result.append(s)
		else:
			c = base.encode('ascii')
			if uppercase:
				c = c.upper()
			result.append(c)
		if toneidx >= 0:
			result.append(tonemarkset[toneidx].encode('ascii'))
	return ''.join(result)
def uni2viqr(ustr):
	ustr = normalize('NFC', ustr)
	result = []
	for c in ustr:
		if c in upperalphas:
			uppercase = True
			c = upper2lower[c]
		elif c in loweralphas:
			uppercase = False
		else:
			if ord(c) < 0x80:
				result.append(chr(ord(c)))
			else:
				result.append(c)
			continue
		base = c
		toneidx = -1
		for k, v in tonetransform.iteritems():
			if c in v:
				base = k
				toneidx = v.index(c)
				break
		if revcompoundtrasformviqr.has_key(base):
			s = revcompoundtrasformviqr[base].encode('ascii')
			if uppercase:
				result.append(lower2upper[s[0]] + s[1:])
			else:
				result.append(s)
		else:
			c = base.encode('ascii')
			if uppercase:
				c = c.upper()
			result.append(c)
		if toneidx >= 0:
			result.append(tonemarksetviqr[toneidx].encode('ascii'))
	return ''.join(result)

if __name__ == '__main__':
	import sys, os.path
	try:
		while True:
			s = raw_input('Input VIQR: ')
			print `viqr2uni(s)`
			print uni2viqr(viqr2uni(s))
			assert s.lower() == uni2viqr(viqr2uni(s)).lower()
			#s = raw_input('Input Telex: ')
			#print `telex2uni(s)`
			#print uni2telex(telex2uni(s))
			#assert s.lower() == uni2telex(telex2uni(s)).lower()
	except EOFError:
		pass

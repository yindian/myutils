#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path

def showhelp():
	print "Usage: %s [-n] file1 file2" % (os.path.basename(sys.argv[0]))
	print "Compare two babylon bbl file. -n to normalize before compare"
	print "Specialized for kangxi dictionary"
	sys.exit(0)

def readbbl(fname):
	f = open(fname, 'r')
	state = 0
	result = None
	output = []
	lineno = 0
	for line in f:
		lineno += 1
		if line[-1] == u'\n':
			line = line[:-1]
		line = unicode(line, 'utf-8')
		if not line and state == 1:
			state = 0
			if result:
				output.append((result[0], u''.join(
					result[1:])))
				result = None
			else:
				print >> sys.stderr, 'Empty line',\
						lineno, 'ignored'
		elif not line:
			print >> sys.stderr, 'Ignore empty line', lineno
		elif state == 0:
			result = [line]
			state = 1
		else:
			result.append(line.replace('<br>', '\n'))
	if result:
		output.append((result[0], u''.join(
			result[1:])))
	f.close()
	return output

def normalizedic(diclist):
	reversed = [(value, key) for key, value in diclist]
	reversed.sort()
	output = []
	lastv = lastk = None
	for value, key in reversed:
		if value == lastv:
			t = key.split('|')
			for k in t:
				lastk[k] = True
		else:
			if lastv is None or lastk is None:
				assert lastk is None
				assert lastv is None
			else:
				t = lastk.keys()
				t.sort()
				output.append(['|'.join(t), lastv])
			lastv = value
			lastk = {}
			t = key.split('|')
			for k in t:
				lastk[k] = True
	if lastv is None or lastk is None:
		assert lastk is None
		assert lastv is None
	else:
		t = lastk.keys()
		t.sort()
		output.append(['|'.join(t), lastv])
	d = {}
	for key, value in output:
		d[key] = d.get(key, 0) + 1
	result = []
	dd = {}
	for key, value in output:
		if d[key] <= 1:
			result.append((key, value))
		else:
			dd[key] = dd.get(key, 0) + 1
			result.append((key+`dd[key]`, value))
	return result

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

def roughcompareline(line1, line2):
	line1 = filter(iscjk, line1)
	line2 = filter(iscjk, line2)
	#print >> sys.stderr, 'Comparing ',
	#writeunicode(line1, sys.stderr, False)
	#print >> sys.stderr, ' with ',
	#writeunicode(line2, sys.stderr)
	if line1 == line2:
		return True
	else:
		if abs(len(line1) - len(line2)) <= 2 and len(line1) > 3:
			if line1.startswith(line2) or line2.startswith(line1):
				return True
		return False

def roughcompare(str1, str2):
	if not str1 or not str2:
		return False
	a = str1.splitlines()
	b = str2.splitlines()
	if abs(len(str1) - len(str2)) > (abs(len(a) - len(b))<<2)+5:
		tryit = False
		if 0 < len(a) - len(b) <= 2:
			if (len(''.join(a[:len(b)]))-len(str2)) < 5:
				tryit = True
		elif 0 < len(b) - len(a) <= 2:
			if (len(''.join(b[:len(a)]))-len(str1)) < 5:
				tryit = True
		if not tryit:
			#print >> sys.stderr, 'Lengh mismatch', len(a), len(b)
			return False
	i = j = 0
	while i < len(a) and j < len(b):
		if roughcompareline(a[i], b[j]):
			i += 1
			j += 1
		elif i+1 < len(a) and roughcompareline(a[i+1], b[j]):
			i += 2
			j += 1
		elif j+1 < len(b) and roughcompareline(a[i], b[j+1]):
			i += 1
			j += 2
		else:
			return False
	return True

try:
	fnenc = 'utf-8'
	from ctypes import windll
	from ctypes.wintypes import DWORD
	STD_OUTPUT_HANDLE = DWORD(-11)
	STD_ERROR_HANDLE = DWORD(-12)
	GetStdHandle = windll.kernel32.GetStdHandle
	WriteConsoleW = windll.kernel32.WriteConsoleW

	def writeunicode(ustr, file=sys.stdout, newline=True):
		if file in (sys.stdout, sys.stderr) and file.isatty():
			which = file==sys.stdout and STD_OUTPUT_HANDLE or STD_ERROR_HANDLE;
			handle = GetStdHandle(which)
			if not isinstance(ustr, unicode):
				ustr = unicode(ustr)
			WriteConsoleW(handle, ustr, len(ustr), None, 0)
			if newline:
				print >> file
		else:
			if newline:
				print >> file, ustr.encode(fnenc, 'replace')
			else:
				file.write(ustr.encode(fnenc, 'replace'))
except:
	def writeunicode(ustr, file=sys.stdout, newline=True):
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

def writeunilines(lines, file=sys.stdout, newline=True):
	for line in lines:
		writeunicode(line, file, newline)

assert __name__ == '__main__'
if len(sys.argv) != 3 and (len(sys.argv) != 4 or sys.argv[1] != '-n'):
	showhelp()
if sys.argv[1] == '-n':
	print 'Reading', sys.argv[2], '...'
	d1 = dict(normalizedic(readbbl(sys.argv[2])))
	print 'Reading', sys.argv[3], '...'
	d2 = dict(normalizedic(readbbl(sys.argv[3])))
	del sys.argv[1]
else:
	print 'Reading', sys.argv[1], '...'
	d1 = dict(readbbl(sys.argv[1]))
	print 'Reading', sys.argv[2], '...'
	d2 = dict(readbbl(sys.argv[2]))

print 'Compare key difference...'
keys1 = set(d1.keys())
keys2 = set(d2.keys())
kdif1 = list(keys1 - keys2)
kdif1.sort()
print 'Keys in %s but not in %s:' % tuple(sys.argv[1:3])
writeunilines(kdif1)
kdif2 = list(keys2 - keys1)
kdif2.sort()
print 'Keys in %s but not in %s:' % tuple(sys.argv[2:0:-1])
writeunilines(kdif2)

#print roughcompare(d1[u'亚'], d2[u'亞'])
#print roughcompare(d1[u'忄'], d2[u'〈忄柬〉'])
#sys.exit(0)

swap = True
for key in kdif1:
	if key.find('|') >= 0:
		swap = False
		break
if swap:
	d1, d2 = d2, d1
	keys1, keys2 = keys2, keys1
	kdif1, kdif2 = kdif2, kdif1
	sys.argv[1:3] = sys.argv[2:0:-1]

kmap21 = {}
kmap12 = {}
for k2 in kdif2:
	for k1 in kdif1:
		if k1.find(k2+'|') >= 0 or k1.find('|'+k2) >= 0:
			kmap21[k2] = k1
			kmap12[k1] = k2
print 'Keys in %s but not in %s considering synonym:' % tuple(sys.argv[1:3])
kd1 = []
for k in kdif1:
	if not kmap12.has_key(k):
		writeunicode(k)
		kd1.append(k)
print 'Keys in %s but not in %s considering synonym:' % tuple(sys.argv[2:0:-1])
kd2 = []
for k in kdif2:
	if not kmap21.has_key(k):
		writeunicode(k)
		kd2.append(k)

kdif1 = []
kdif2 = []
print 'Trying to find mapping for uniq keys: %s to %s...' % tuple(sys.argv[1:3])
for k in kd1:
	writeunicode(k, sys.stdout, False)
	print 'finding...'
	found = False
	for key, val in d2.iteritems():
		if roughcompare(d1[k], val):
			found = True
			kmap12[k] = key
			#kmap21[key] = k
			#print >> sys.stderr, 'Found match ',
			#writeunicode(d1[k], sys.stderr, False)
			#print >> sys.stderr, ' with ',
			#writeunicode(val, sys.stderr)
			print 'Found mapping: ',
			writeunicode(k, sys.stdout, False)
			print ' -> ',
			writeunicode(key)
			break
	if not found:
		kdif1.append(k)
print 'Trying to find mapping for uniq keys: %s to %s...' % tuple(sys.argv[2:0:-1])
for k in kd2:
	writeunicode(k, sys.stdout, False)
	print 'finding...'
	found = False
	for key, val in d1.iteritems():
		if roughcompare(d2[k], val):
			found = True
			kmap21[k] = key
			#kmap12[key] = k
			#print >> sys.stderr, 'Found match ',
			#writeunicode(d2[k], sys.stderr, False)
			#print >> sys.stderr, ' with ',
			#writeunicode(val, sys.stderr)
			print 'Found mapping: ',
			writeunicode(k, sys.stdout, False)
			print ' -> ',
			writeunicode(key)
			break
	if not found:
		kdif2.append(k)

print 'Keys in %s but not in %s after mapping:' % tuple(sys.argv[1:3])
kdif1 = kd1[:]
kd1 = []
for k in kdif1:
	if not kmap12.has_key(k):
		writeunicode(k)
		kd1.append(k)
print 'Keys in %s but not in %s after mapping:' % tuple(sys.argv[2:0:-1])
kdif2 = kd2[:]
kd2 = []
for k in kdif2:
	if not kmap21.has_key(k):
		writeunicode(k)
		kd2.append(k)

print 'Keys mapping from %s to %s:' % tuple(sys.argv[1:3])
for k in kmap12.keys():
	writeunicode(k, sys.stdout, False)
	print ' -> ',
	writeunicode(kmap12[k])
print 'Keys mapping from %s to %s:' % tuple(sys.argv[2:0:-1])
for k in kmap21.keys():
	writeunicode(k, sys.stdout, False)
	print ' -> ',
	writeunicode(kmap21[k])

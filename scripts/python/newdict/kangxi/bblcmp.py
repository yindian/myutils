#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path

def showhelp():
	print "Usage: %s [-n] file1 file2" % (os.path.basename(sys.argv[0]))
	print "Compare two babylon bbl file. -n to normalize before compare"
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

def iscjk(str):
	for c in str:
		p = ord(c)
		if 0x4e00 <= p <= 0x9fc3 or 0x3400 <= p <= 0x4db5 or\
			0xf900 <= p <= 0xfad9 or 0x20000 <= p <= 0x2a6d6 or\
			0x2f800 <= p <= 0x2fa1d or p == 0x3007: # CJK characters
			pass
		elif 0xD800 <= p <= 0xDFFF: # surrogate pair for narrow python
			pass
		#elif c in u'{/@}|':
		#	pass
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

	def writeunicode(ustr, file, newline=True):
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
	def writeunicode(ustr, file, newline=True):
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
else:
	print 'Reading', sys.argv[1], '...'
	d1 = dict(readbbl(sys.argv[1]))
	print 'Reading', sys.argv[2], '...'
	d2 = dict(readbbl(sys.argv[2]))

print 'Compare key difference...'
keys1 = set(d1.keys())
keys2 = set(d2.keys())
kdiff = list(keys1 - keys2)
kdiff.sort()
print 'Keys in %s but not in %s:' % tuple(sys.argv[1:3])
writeunilines(kdiff)
kdiff = list(keys2 - keys1)
kdiff.sort()
print 'Keys in %s but not in %s:' % tuple(sys.argv[2:0:-1])
writeunilines(kdiff)

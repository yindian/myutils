#!/usr/bin/env python
import sys, string, os, os.path, glob
def win32_utf8_argv():
	try:
		from ctypes import POINTER, byref, cdll, c_int, windll
		from ctypes.wintypes import LPCWSTR, LPWSTR

		GetCommandLineW = cdll.kernel32.GetCommandLineW
		GetCommandLineW.argtypes = []
		GetCommandLineW.restype = LPCWSTR

		CommandLineToArgvW = windll.shell32.CommandLineToArgvW
		CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
		CommandLineToArgvW.restype = POINTER(LPWSTR)

		cmd = GetCommandLineW()
		argc = c_int(0)
		argv = CommandLineToArgvW(cmd, byref(argc))
		if argc.value > 0:
			# Remove Python executable if present
			assert argc.value >= len(sys.argv)
			start = argc.value - len(sys.argv)
			return [argv[i].encode('utf-8') for i in
					xrange(start, argc.value)]
	except Exception:
		pass

def showhelp():
	me = os.path.basename(sys.argv[0])
	print "%s conversion rename from one encoding to another" % (me)
	print "Usage: %s from_enc to_enc files" % (me)
	print "Using same encoding for both from and to will normalize filenames"

fnenc = sys.getfilesystemencoding()

try:
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
		if type(ustr) == type(''):
			if newline:
				print >> file, ustr
			else:
				file.write(ustr)
			return
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

def renameit(path, fromenc, toenc):
	dest = path
	try:
		if os.name != 'nt':
			ansi = path.decode(fnenc).encode(fromenc)
		else:
			ansi = path.encode(fromenc)
	except UnicodeDecodeError:
		ansi = path
	except UnicodeEncodeError:
		if fromenc == toenc:
			ansi = path.encode(toenc, 'replace').replace('?', '_')
		else:
			print >> sys.stderr, 'Not of encoding %s: ' % (fromenc), 
			writeunicode(path, sys.stderr)
			raise
	global errors
	try:
		dest = unicode(ansi, toenc, errors)
	except UnicodeDecodeError:
		print >> sys.stderr, 'Cannot convert from %s to %s: ' % (fromenc,
				toenc), 
		writeunicode(path, sys.stderr)
		raise
	if os.name != 'nt':
		dest = dest.encode(fnenc, errors)
	return (path, dest)

todolist = []

def convren((fromenc, toenc), dirname, names):
	for name in names:
		todolist.append(renameit(os.path.join(dirname, name), fromenc, toenc))

import encodings, codecs, urllib
class Codec(codecs.Codec):
	def encode(self,input,errors='strict'):
		return urllib.quote(input.encode('utf-8')).encode('ascii'), len(input)
	def decode(self,input,errors='strict'):
		return urllib.unquote(str(input)).decode('utf-8', errors), len(input)
class IncrementalEncoder(codecs.IncrementalEncoder):
	def encode(self, input, final=False):
		return urllib.quote(input.encode('utf-8')).encode('ascii')
class IncrementalDecoder(codecs.IncrementalDecoder):
	def decode(self, input, final=False):
		return urllib.unquote(str(input)).decode('utf-8', errors)
class StreamWriter(Codec,codecs.StreamWriter): pass
class StreamReader(Codec,codecs.StreamReader): pass
encodings._cache['utf-8-url'] = codecs.CodecInfo(
		name='utf-8-url',
		encode=Codec().encode,
		decode=Codec().decode,
		incrementalencoder=IncrementalEncoder,
		incrementaldecoder=IncrementalDecoder,
		streamreader=StreamReader,
		streamwriter=StreamWriter,
		)
def unxmlcharref(s):
	ar = s.split('&#')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.find(';')
		if p > 0 and s[:p].isdigit():
			result.append(unichr(int(s[:p])))
			result.append(s[p+1:])
		elif p > 0 and s[0] == 'x':
			result.append(unichr(int(s[1:p], 16)))
			result.append(s[p+1:])
		else:
			result.append(u'&#')
			result.append(s)
	return u''.join(result)
class Codec(codecs.Codec):
	def encode(self,input,errors='strict'):
		return input.encode('ascii', 'xmlcharrefreplace'), len(input)
	def decode(self,input,errors='strict'):
		return unxmlcharref(str(input)), len(input)
class IncrementalEncoder(codecs.IncrementalEncoder):
	def encode(self, input, final=False):
		return input.encode('ascii', 'xmlcharrefreplace')
class IncrementalDecoder(codecs.IncrementalDecoder):
	def decode(self, input, final=False):
		return unxmlcharref(str(input))
class StreamWriter(Codec,codecs.StreamWriter): pass
class StreamReader(Codec,codecs.StreamReader): pass
encodings._cache['xmlcharref'] = codecs.CodecInfo(
		name='xmlcharref',
		encode=Codec().encode,
		decode=Codec().decode,
		incrementalencoder=IncrementalEncoder,
		incrementaldecoder=IncrementalDecoder,
		streamreader=StreamReader,
		streamwriter=StreamWriter,
		)
try:
	import json
except:
	import simplejson as json
class Codec(codecs.Codec):
	def encode(self,input,errors='strict'):
		return json.dumps(input)[1:-1], len(input)
	def decode(self,input,errors='strict'):
		return json.loads('"%s"' % (str(input),)), len(input)
class IncrementalEncoder(codecs.IncrementalEncoder):
	def encode(self, input, final=False):
		return json.dumps(input)[1:-1]
class IncrementalDecoder(codecs.IncrementalDecoder):
	def decode(self, input, final=False):
		return json.loads('"%s"' % (str(input),))
class StreamWriter(Codec,codecs.StreamWriter): pass
class StreamReader(Codec,codecs.StreamReader): pass
encodings._cache['json'] = codecs.CodecInfo(
		name='json',
		encode=Codec().encode,
		decode=Codec().decode,
		incrementalencoder=IncrementalEncoder,
		incrementaldecoder=IncrementalDecoder,
		streamreader=StreamReader,
		streamwriter=StreamWriter,
		)

if __name__ == '__main__':
	argv = win32_utf8_argv() or sys.argv
	if os.name != 'nt':
		zstr = ''
	else:
		zstr = u''
		argv = map(lambda s:unicode(s, 'utf-8'), argv)
	if len(argv) < 4:
		showhelp()
		sys.exit(0)
	fromenc = argv[1]
	assert ''.encode(fromenc) == ''
	toenc = argv[2]
	assert ''.encode(toenc) == ''
	if argv[3] == '-f':
		errors = 'ignore'
		del argv[3]
	else:
		errors = 'strict'

	for file in argv[3:]:
		if os.path.exists(file):
			convren((fromenc, toenc), zstr, [file])
			os.path.walk(file, convren, (fromenc, toenc))
		else:
			files = glob.glob(file)
			for file in files:
				if not isinstance(file, unicode):
					file = unicode(file, fnenc)
				convren((fromenc, toenc), zstr, [file])
				os.path.walk(file, convren, (fromenc, toenc))
			if not files:
				print >> sys.stderr, 'No such file or directory: ',
				writeunicode(file, sys.stderr)

	if todolist:
		smap = {}
		dmap = {}
		for from_, to_ in todolist:
			smap[from_] = None
		result = []
		for from_, to_ in todolist:
			if from_ == to_: continue
			srcdir, srcfile = os.path.split(from_)
			dstdir, dstfile = os.path.split(to_)
			if srcfile == dstfile: continue
			if smap.has_key(srcdir) and smap[srcdir] is not None:
				to_ = os.path.join(smap[srcdir], dstfile)
			if smap.has_key(to_) or dmap.has_key(to_):
				i = 2
				while smap.has_key(to_+'~%d'%i) or dmap.has_key(to_+'~%d'%i):
					i += 1
				to_ = to_ + '~%d'%i
				smap[from_] = to_
			result.append((from_, to_, os.path.join(dstdir, srcfile)))
			dmap[to_] = None

		for from_, to_, tmp in result:
			writeunicode(from_, sys.stdout, False)
			print ' => ',
			writeunicode(to_, sys.stdout, True)
		choice = raw_input('Are you sure to convert?')
		if choice.lower() in ('yes', 'y'):
			for tmp, to_, from_ in result:
				writeunicode(from_, sys.stdout, False)
				print ' => ',
				writeunicode(to_, sys.stdout, True)
				os.rename(from_, to_)
			print 'Done'
		else:
			print 'User canceled'
	else:
		print >> sys.stderr, 'Error: no files found'

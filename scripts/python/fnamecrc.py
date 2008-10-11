from binascii import *
from glob import glob
import sys, os, string

def myescape(str):
	str = str.replace('[', r'?')
	str = str.replace(']', r'?')
	return str

if len(sys.argv) < 2:
	print "Usage: %s [-r] filename" % (sys.argv[0])
	print "Remove CRC32 in filename, or put CRC32 in filename when -r"
	sys.exit()

if sys.argv[1].lower() == '-r':
	reverse = True
	filenames = sys.argv[2]
else:
	reverse = False
	filenames = sys.argv[1]

l = glob(filenames)
if not l:
	l = glob(myescape(filenames))

if not l:
	print "Warning: empty file list"

alltrans = string.maketrans('', '')
chunksize = 1024**2 * 16

for fname in l:
	try:
		#print "File %s" % fname
		expected = fname[fname.rfind('[')+1:fname.rfind(']')].upper()
		#print "CRC should be %s" % expected
		if not reverse:
			assert expected != ''
			assert expected.translate(alltrans, string.hexdigits) == ''
		f = open(fname, 'rb')
		cksum = 0
		s = f.read(chunksize)
		while s:
			cksum = crc32(s, cksum)
			s = f.read(chunksize)
		f.close()
		if cksum < 0:
			cksum += 2**32
		#print "CRC is %08X (%d)" % (cksum, cksum)
		s = "%08X" % cksum
		if reverse:
			fnamenew = fname[:fname.rfind('[')+1] + s + \
					fname[fname.rfind(']'):]
			os.rename(fname, fnamenew)
			print "File %s renamed to %s" % (fname, fnamenew)
		else:
			if expected != s:
				print "%s, expect %s, but get %s" % (fname, expect, s)
				raise
			#print "File %s OK" % (fname)
			fnamenew = fname[:fname.rfind('[')+1] + \
					fname[fname.rfind(']'):]
			os.rename(fname, fnamenew)
			print "File %s renamed to %s" % (fname, fnamenew)
	except:
		print >> sys.stderr, "Error processing %s" % fname
		continue

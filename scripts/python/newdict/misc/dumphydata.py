#!/usr/bin/env python
import sys, glob, os.path, os, struct
if __name__ == '__main__':
	assert len(sys.argv) > 1
	filelist = glob.glob(sys.argv[1])
	for filename in filelist:
		basename = os.path.basename(filename)
		try:
			basename = basename[:basename.index('.')]
		except ValueError:
			pass
		print 'Dumping %s...' % (filename),
		ret = os.system('windres -i "%s" -o "%s"' % (filename, basename+'.res'))
		if ret != 0:
			print 'Error %d executing windres' % (ret)
			continue
		resbin = open(basename+'.res', 'rb').read()
		pos = 0
		while True:
			found = False
			while not found:
				datalen = struct.unpack('L', resbin[pos:pos+4])[0]
				headerlen = struct.unpack('L', resbin[pos+4:pos+8])[0]
				p = pos + 8
				typestr = ''
				while resbin[p:p+2] != '\0\0':
					typestr += resbin[p:p+2]
					p += 2
				typestr = unicode(typestr, 'utf-16le')
				p += 2
				namestr = ''
				while resbin[p:p+2] != '\0\0':
					namestr += resbin[p:p+2]
					p += 2
				namestr = unicode(namestr, 'utf-16le')
				if typestr == u'WAV':
					found = True
				else:
					pos += datalen + headerlen
					if pos >= len(resbin):
						break
			if not found:
					break
			wavbin = resbin[pos+headerlen:pos+headerlen+datalen]
			f = open(basename+'_'+namestr+'.wav', 'wb')
			f.write(wavbin)
			f.close()
			pos += datalen + headerlen
		print 'done.'

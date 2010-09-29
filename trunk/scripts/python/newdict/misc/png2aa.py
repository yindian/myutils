#!/usr/bin/env python
import sys, os.path, glob
import png

assert __name__ == '__main__'

if len(sys.argv) < 2:
	print 'Usage: %s png_files' % (sys.argv[0],)
	sys.exit(0)

for fnpat in sys.argv[1:]:
	for fname in glob.glob(fnpat):
		r = png.Reader(filename=fname)
		w, h, px, met = r.asRGB()
		for line in px:
			assert len(line) % 3 == 0
			for i in xrange(len(line) / 3):
				val = sum(line[i*3: (i+1)*3])
				if val > 650:
					sys.stdout.write(' ')
				else:
					sys.stdout.write('#')
			sys.stdout.write('\n')

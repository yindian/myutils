#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, struct, time

outbase = 'out'

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s xmldumpfile" % (sys.argv[0])
		print "Build stardict dictionary out of mediawiki xml dump"
		sys.exit(0)

	print >> sys.stderr, 'Generating title list...',
	timestart = time.clock()
	f = open(sys.argv[1], 'r')
	g = open(outbase + '.key', 'w')
	for line in f:
		if line.startswith('    <title>'):
			key = line[11:line.find('</title>')]
			if key.startswith('Wikipedia:') or key.startswith('Help:') \
					or key.startswith('画像:') or key.startswith('Portal:') \
					or key.startswith('Template:') or key.startswith('MediaWiki:') \
					or key.startswith('WP:') or key.startswith('Image:'):
				continue
			print >> g, '%s\t%X' % (key, f.tell() >> 10)
	f.close()
	g.close()
	timeend = time.clock()
	print >> sys.stderr, 'done\t\tuser time consumed: %.f' % (timeend - timestart)

	print >> sys.stderr, 'Building index of',
	timestart = time.clock()
	f = open(outbase + '.key', 'r')
	lines = f.readlines()
	tell = f.tell()
	f.close()
	print >> sys.stderr, 'size %d...' % (tell),
	items = []
	oldtell = tell = 0
	for line in lines:
		line = line[:-1].split('\t')
		assert len(line) == 2
		if (long(line[1], 16)) > tell:
			oldtell = tell << 10
			tell = long(line[1], 16)
		items.append([line[0], oldtell, tell << 10])
	del lines
	items.sort()
	g = open(outbase + '.itm', 'w')
	for item in items:
		print >> g, '%s\t%X\t%X' % (item[0], item[1], item[2])
	g.close()
	timeend = time.clock()
	print >> sys.stderr, 'done\t\tuser time consumed: %.f' % (timeend - timestart)

	print >> sys.stderr, 'Building dic...',
	timestart = time.clock()
	f = open(sys.argv[1], 'rb')
	s = f.readline()
	if s.endswith('\r\n'):
		deleol = -2
		eol = '\r\n'
	else:
		deleol = -1
		eol = '\n'
	ifofile = open('out.ifo', 'wb')
	idxfile = open('out.idx', 'wb')
	dicfile = open('out.dic', 'wb')

	for item in items:
		f.seek(item[1])
		start = '    <title>' + item[0] + '</title>'
		for line in f:
			if line.startswith(start) or f.tell() > item[2] + 20480:
				break
		if not line.startswith(start):
			tell = item[1] - 20480
			if tell < 0: tell = 0
			f.seek(tell)
			start = '    <title>' + item[0]
			for line in f:
				if line.startswith(start) or f.tell() > item[2] + 20480:
					break
		assert f.tell() <= item[2] + 20480
		assert line.startswith(start)
		for line in f:
			if line.startswith('      <text') or line.startswith('    <title>'):
				break
		assert line.startswith('      <text')
		end = '</text>' + eol
		if line.endswith(end):
			text = line[line.index('>')+1:line.index('</text>')]
		else:
			lines = [line[line.index('>')+1:]]
			for line in f:
				if line.endswith(end):
					break
				lines += [line]
			assert line.endswith(end)
			lines += [line[:line.index('</text>')]]
			text = ''.join(lines)
		#line = f.readline()[:deleol].split('\t')
		#line[1] = line[1].replace('<br>\\n', '\n')
		offset_old = dicfile.tell()
		dicfile.write(text)
		idxfile.write(item[0])
		idxfile.write('\0')
		idxfile.write(struct.pack('>LL', offset_old, len(text)))
	f.close()
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=w\n" % (len(items), idxfile.tell(), sys.argv[0]+' output'))
	ifofile.close()
	idxfile.close()
	dicfile.close()
	timeend = time.clock()
	print >> sys.stderr, 'done\t\tuser time consumed: %.f' % (timeend - timestart)
	print >> sys.stderr, 'All done.'

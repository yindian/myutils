#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, socket, struct

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: %s indexfile tabfile" % (sys.argv[0])
		print "Build stardict dictionary by tabfile & its index"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	lines = f.readlines()
	f.close()
	#lines = [line.split('\t') for line in lines]
	items = []
	for line in lines:
		line = line.split('\t')
		items.append([line[0].lower(), line[0], int(line[1], 16)])
	del lines
	items.sort()

	print >> sys.stderr, 'Sorting done. Now building dic'
	f = open(sys.argv[2], 'rb')
	s = f.readline()
	if s.endswith('\r\n'):
		deleol = -2
	else:
		deleol = -1
	f.close()
	f = open(sys.argv[2], 'rb')
	ifofile = open('out.ifo', 'wb')
	idxfile = open('out.idx', 'wb')
	dicfile = open('out.dict', 'wb')

	itemnum = 0
	for item in items:
		f.seek(item[-1])
		line = f.readline()[:deleol].split('\t', 1)
		if not line[0] or not line[1]: continue
		itemnum += 1
		line[1] = line[1].replace('\\n', '\n')
		offset_old = dicfile.tell()
		dicfile.write(line[1])
		idxfile.write(line[0])
		idxfile.write('\0')
		idxfile.write(struct.pack('>LL', offset_old, len(line[1])))
	f.close()
	ifofile.write("StarDict's dict ifo file\nversion=2.4.2\nwordcount=%d\nidxfilesize=%ld\nbookname=%s\nsametypesequence=m\n" % (itemnum, idxfile.tell(), sys.argv[0]+' output'))
	ifofile.close()
	idxfile.close()
	dicfile.close()
	print >> sys.stderr, 'All done.'

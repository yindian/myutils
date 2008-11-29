#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
titlecode = 0x0100
endcode = 0x0001

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict tab text format"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	state = laststate = 0
	chgflag = False
	lastline = None
	for line in f:
		if line.startswith(stopcodestr):
			laststate = state
			lastline = None
			line = line.split()
			code1 = int(line[2], 0)
			code2 = int(line[3], 0)
			if code1 == wordcode:
				state = 0
				chgflag = True
			elif code1 == itemcode:
				assert 1 <= code2 <= 10
				state = code2
				chgflag = True
			else:
				raise 'Unknown code %d' % (code1)
		else:
			if chgflag:
				chgflag = False
				if state == 0:
					sys.stdout.write('\n')
				elif laststate == 0:
					sys.stdout.write('\t')
				else:
					pass
			else:
				if not lastline is None:
					sys.stdout.write(lastline)
					if state > 0:
						sys.stdout.write('<br>\\n')
			if line.endswith('\r\n'):
				lastline = line[:-2]
			else:
				lastline = line[:-1]
	f.close()

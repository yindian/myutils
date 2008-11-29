#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
kanacode = 0x0130
kanjicod = 0x0260
mixedcod = 0x0160
endcode = 0x0001

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict babylon text format"
		print "This version is specialized for Kojien 6"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	state = laststate = kanacode
	chgflag = False
	lastline = None
	titleline = ''
	for line in f:
		if line.startswith(stopcodestr):
			laststate = state
			oldlastline = lastline
			lastline = None
			line = line.split()
			code1 = int(line[2], 0)
			code2 = int(line[3], 0)
			if code1 == wordcode:
				assert code2 in (kanacode, kanjicod, mixedcod)
				state = code2
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
				if state in (kanacode, mixedcod):
					#sys.stdout.write('\n')
					sys.stdout.write('\n\n')
				elif state == kanjicod:
					assert laststate == kanacode
					lastline = oldlastline
					if not lastline is None:
						sys.stdout.write(lastline)
				elif laststate in (kanacode, kanjicod, mixedcod) and 1 <= state <= 10:
					#sys.stdout.write('\t')
					sys.stdout.write('\n')
					sys.stdout.write(titleline)
					sys.stdout.write('<br>')
					titleline = ''
				else:
					# mixedcod not dealt with. left for post processing
					pass
			else:
				if not lastline is None:
					sys.stdout.write(lastline)
					if not state in (kanacode, kanjicod, mixedcod):
						#sys.stdout.write('\\n')
						sys.stdout.write('<br>')
			if line.endswith('\r\n'):
				lastline = line[:-2]
			else:
				lastline = line[:-1]
			if state in (kanacode, kanjicod, mixedcod):
				titleline += lastline
			if state == kanacode and lastline != '':
				lastline = unicode(lastline, 'utf-8')
				if lastline[-1] == u'\u3010':
					lastline = lastline[:-1] + u'|'
				lastline = lastline.replace(u'\u2010', u'')
				lastline = lastline.replace(u'\u30fb', u'')
				lastline = lastline.encode('utf-8')
			elif state == kanjicod and lastline != '':
				lastline = unicode(lastline, 'utf-8')
				if lastline[-1] == u'\u3011':
					lastline = lastline[:-1]
				if lastline.find(u'\u3011') >= 0:
					lastline = lastline[:lastline.find(u'\u3011')]
				if lastline.find(u'\u30fb') >= 0:
					lastline = lastline.replace(u'\u30fb', u'|')
				lastline = lastline.encode('utf-8')
	f.close()

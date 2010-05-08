#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string
import pdb

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0160
begcode = 0x0002
m1 = 0x0005
m2 = 0x0004
endcode = 0x0001

def gettitle(lines, state):
	try:
		assert state == begcode or state == m2
		assert len(lines) == 2
		assert lines[1] == ''
	except:
		pdb.set_trace()
	return lines[0].strip()

def output_entry(word, origtitle, *mean):
	sys.stdout.write(word)
	sys.stdout.write('\t')
	sys.stdout.write('\\n'.join(mean))
	sys.stdout.write('\n')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict babylon text format"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	state = laststate = keycode
	chgflag = False
	lastline = None
	titleline = []
	wordcount = 0
	finaldic = []
	result = None
	for line in f:
		if line.startswith(stopcodestr):
			laststate = state
			oldlastline = lastline
			assert lastline == ''
			lastline = None
			line = line.split()
			code1 = int(line[2], 0)
			code2 = int(line[3], 0)
			if code1 == wordcode:
				assert code2 in (keycode,)
				state = code2
				chgflag = True
			elif code1 == itemcode:
				assert code2 in (begcode, m1, m2, endcode)
				state = code2
				chgflag = True
			else:
				raise 'Unknown code %d' % (code1)
		else:
			if chgflag:
				chgflag = False
				if state == keycode:
					assert result is not None
					finaldic.append(result)
					result = None
				elif laststate == keycode and state in (begcode
						, m1, m2, endcode):
					assert result is None
					result = [gettitle(titleline, state)]
					if titleline[-1] == '':
						del titleline[-1]
					result.extend(titleline)
					titleline = []
					wordcount += 1
				elif laststate == keycode:
					raise 'Invalid state %04x after %04x' %(
							state, laststate)
				elif state in (begcode, m1, m2): pass
				elif state == endcode: pass
				else:
					raise 'Unknown state %04x after %04x' %(
							state, laststate)
			else:
				if lastline is not None and state != keycode:
					result.append(lastline)
			if line.strip() and state in (begcode, m1, m2):
				line = ' ' * state + line
			if line.endswith('\r\n'):
				lastline = line[:-2]
			else:
				lastline = line[:-1]
			if state == keycode:
				titleline += [lastline]
	if result is not None:
		if lastline and result[-1] != lastline:
			result.append(lastline)
		finaldic.append(result)
	f.close()
	print >> sys.stderr, 'Word count =', wordcount
	for entry in finaldic:
		output_entry(*entry)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, re
import pdb, traceback

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0160
begcode = 0x0003
m1 = 0x0005
m2 = 0x0004
endcode = 0x0001

var = re.compile(u'(.)（(.)）')
var2 = re.compile(u'(..)（(..)）')
var3 = re.compile(u'(...)（(...)）')
var4 = re.compile(u'(.)（(.)・(.)）')
alt = re.compile(u'(.)〔?｛(.)｝〕?')
alt2 = re.compile(u'(..)｛(..)｝')
alt3 = re.compile(u'(.)｛(.)・(.)｝')
varalt = re.compile(u'(.)〔?（(.)）｛(.)｝〕?')

def gettitle(lines, state):
	try:
		assert state == begcode or state == m2
		assert len(lines) == 2
		assert lines[1] == ''
	except:
		pdb.set_trace()
	return lines[0].strip()

def output_entry(word, origtitle, *mean):
	s = word.decode('utf-8')
	if s.startswith(u'【'):
		assert s.endswith(u'】')
		s = s[1:-1]
		if s.find(u'（') > 0 or s.find(u'｛') > 0:
			t = alt.sub(r'\g<2>', varalt.sub(r'\g<3>', s))
			s = alt.sub(r'\g<1>', varalt.sub(r'\g<1>', s))
			t = alt2.sub(r'\g<2>', var.sub(r'\g<1>', t))
			s = alt2.sub(r'\g<1>', var.sub(r'\g<1>', s))
			t = var3.sub(r'\g<1>', var2.sub(r'\g<1>', t))
			s = var3.sub(r'\g<1>', var2.sub(r'\g<1>', s))
			t = var4.sub(r'\g<1>', t)
			s = var4.sub(r'\g<1>', s)
			ss = alt3.sub(r'\g<1>', s)
			if s != ss:
				s = ss
				t1 = alt3.sub(r'\g<2>', t)
				t2 = alt3.sub(r'\g<3>', t)
				t = t1 + u'|' + t2
			if s != t:
				s = s + u'|' + t
		try:
			assert s.find(u'（') < 0
			assert s.find(u'｛') < 0
			assert s.find(u'〔') < 0
		except:
			traceback.print_exc()
			pdb.set_trace()
	#sys.stdout.write(s.encode('utf-8'))
	variants = [s.encode('utf-8')]
	for line in mean:
		line = line.decode('utf-8')
		if len(line) >= 3 and line[0] == u'【' and line[2] == u'】':
			t = line[1].encode('utf-8')
			if t not in variants:
				variants.append(t)
	if len(variants) > 1:
		try:
			assert len(s) == 1 or (len(s) == 2 and 
					0xD800 <= ord(s[0]) < 0xDC00)
		except:
			traceback.print_exc()
			pdb.set_trace()
	sys.stdout.write('|'.join(variants))
	sys.stdout.write('\t')
	sys.stdout.write(word)
	sys.stdout.write('\\n')
	sys.stdout.write('\\n'.join(mean))
	sys.stdout.write('\n')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict tabfile format"
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

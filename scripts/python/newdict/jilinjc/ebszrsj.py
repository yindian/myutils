#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0160
begcode = 0x0002
endcode = 0x0001

def gettitle(lines, state):
	assert state == begcode
	assert len(lines) == 2
	assert lines[1] == ''
	assert lines[0].endswith('[U]')
	return lines[0][:-4].strip()

def output_entry(word, mean):
	sys.stdout.write(word)
	sys.stdout.write('\n')
	sys.stdout.write('<br>'.join(mean))
	sys.stdout.write('<br>\n\n')

def output_entry(word, mean):
	s = unicode(word, 'utf-8')
	if ord(s[0]) not in range(0x3041, 0x30fb):
		if not (mean[1].startswith('〈句〉') or
				mean[1].startswith('〈連語〉')):
			print >> sys.stderr, 'Warning: not a word or sentence',
			print >> sys.stderr, s.encode('gbk', 'replace'),
			print >> sys.stderr, unicode(mean[1], 'utf-8'
					).encode('gbk', 'replace')
	sys.stdout.write(word.replace('|', ' '))
	sys.stdout.write('\n\t'.join(['']+mean))
	sys.stdout.write('\n')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict babylon text format"
		print "This version is specialized for Jilin JC bilingual"
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
				assert code2 in (begcode, endcode)
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
				elif laststate == keycode and (state == begcode\
						or state == endcode):
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
				elif state in (begcode,): pass
				elif state == endcode: pass
				else:
					raise 'Unknown state %04x after %04x' %(
							state, laststate)
			else:
				if lastline is not None and state != keycode:
					result.append(lastline)
			if line.endswith('\r\n'):
				lastline = line[:-2]
			else:
				lastline = line[:-1]
			if state == keycode:
				titleline += [lastline]
	#sys.stdout.write('\n\n')
	if result is not None:
		finaldic.append(result)
	f.close()
	print >> sys.stderr, 'Word count =', wordcount
	lastword = lastmean = None
	for entry in finaldic:
		if lastword is None:
			lastword = [entry[0]]
			lastmean = entry[1:]
		else:
			identical = entry[-1] == lastmean[-1] and\
					abs(len(entry)-1-len(lastmean)) <= 1
			if identical:
				if len(entry) < 3:
					raise
				elif entry[2] not in lastmean[1:3]:
					#print >> sys.stderr, "Not ident "\
					#"entry[2]=", unicode(entry[2], 'utf-8'
					#).encode('gbk', 'replace'), "lastmean"\
					#"=", unicode(lastmean[1], 'utf-8'
					#).encode('gbk', 'replace'), '|'\
					#'', unicode(lastmean[2], 'utf-8'
					#).encode('gbk', 'replace')
					identical = False
			if not identical:
				if len(lastword) == 1:
					word = lastword[0]
				else:
					word = '|'.join([lastword[-1]]
							+ lastword[:-1])
				output_entry(word, lastmean)
				lastword = [entry[0]]
				lastmean = entry[1:]
			else:
				lastword.append(entry[0])
				lastmean = entry[1:]
	if lastword is not None:
		if len(lastword) == 1:
			word = lastword[0]
		else:
			word = '|'.join(lastword[-1]
					+ lastword[:-1])
		output_entry(word, lastmean)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0091
paracode = 0x0090
begcode = 0x0002
endcode = 0x0001

markchars = u'\u2051*\u2982\uffee\u2192\u237e'

def gettitle(lines, state):
	if lines[0].startswith('【'):
		if lines[0].endswith('】'):
			return lines[0][len('【'):-len('】')]
		pos = lines[0].index('】')
		str = unicode(lines[0][pos+len('】'):], 'utf-8')
		for c in str:
			assert c in markchars
		return lines[0][len('【'):pos]
	else:
		str = unicode(lines[0], 'utf-8')
		try:
			assert lines[0].find('→') >= 0
		except:
			print >>sys.stderr, 'Key field has no arrow'
			print >>sys.stderr, str.encode('gbk', 'replace')
			print >>sys.stderr, 'Directly return'
			return lines[0]
		if str.endswith(u'[\u62e1]'):
			str = str[:-3]
		elif state == endcode:
			str = str[:str.index(u'[\u62e1]')]
		for i in range(len(str)):
			if str[i] in markchars:
				break
		for c in str[i:]:
			try:
				assert c in markchars
			except:
				print >>sys.stderr,'Unexpected key field suffix'
				print >>sys.stderr, str.encode('gbk', 'replace')
				print >>sys.stderr, `c`, '(u%04X)' % (ord(c))
				raise
		str = str[:i]
		if str.find(u'(') < 0:
			return str.encode('utf-8')
		assert str.endswith(u')')
		str = str[:-1].replace(u'(', u'|').replace(u'\u30fb', u'|')
		return str.encode('utf-8')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict babylon text format"
		print "This version is specialized for Shogakukan Zhong-ri"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	state = laststate = keycode
	chgflag = False
	lastline = None
	titleline = []
	wordcount = 0
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
				assert code2 in (keycode, paracode)
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
					sys.stdout.write('\n\n')
				elif laststate == keycode and (state == begcode\
						or state == endcode):
					#sys.stdout.write('\t')
					sys.stdout.write(gettitle(titleline, 
						state))
					sys.stdout.write('\n')
					sys.stdout.write('<br>'.join(titleline))
					titleline = []
					wordcount += 1
				elif laststate == keycode:
					raise 'Invalid state %04x after %04x' %(
							state, laststate)
				elif state in (begcode, paracode): pass
				elif state == endcode: pass
				else:
					raise 'Unknown state %04x after %04x' %(
							state, laststate)
			else:
				if lastline is not None and state != keycode:
					sys.stdout.write(lastline)
					#sys.stdout.write('\\n')
					sys.stdout.write('<br>')
			if line.endswith('\r\n'):
				lastline = line[:-2]
			else:
				lastline = line[:-1]
			if state == keycode:
				titleline += [lastline]
			elif lastline.find('　') >= 0:
				if not lastline.startswith('ＧＢ') and not \
						lastline.startswith('電碼'):
					lastline = lastline.replace('　', 
							'<br>')
					if lastline.endswith('<br>'):
						lastline = lastline[:-4]
				else:
					chunks = lastline.split('　')
					for chunk in chunks:
						assert chunk[-1].isdigit()
	sys.stdout.write('\n\n')
	f.close()
	print >> sys.stderr, 'Word count =', wordcount

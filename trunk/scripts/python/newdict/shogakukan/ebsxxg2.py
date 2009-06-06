#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string
try:
	import psyco
	psyco.full()
except:
	pass

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0160
begcode = 0x0002
endcode = 0x0001
markchars = u'*★'

def removedigit(str):
	result = []
	for c in str:
		if not isallcjk(c):
			try:
				if not c.isdigit():
					assert c in u'【】()―,'
			except:
				print >> sys.stderr, 'str =', str.encode('gbk',
						'replace')
				raise
		else:
			result.append(c)
	return u''.join(result)

def isallcjk(str):
	for c in str:
		p = ord(c)
		if 0x4e00 <= p <= 0x9fc3 or 0x3400 <= p <= 0x4db5 or\
			0xf900 <= p <= 0xfad9 or 0x20000 <= p <= 0x2a6d6 or\
			0x2f800 <= p <= 0x2fa1d or p == 0x3007: # CJK characters
			pass
		elif 0xE100 <= p <= 0xE500: # EUDC gaiji
			pass
		elif 0xD800 <= p <= 0xDFFF: # surrogate pair for narrow python
			pass
		elif c in u'{/@}|':
			pass
		elif p == 0x25cb: # fullwidth circle (zero)
			pass
		else:
			return False
	return True

simp = {}
def gettitle(lines, state):
	if lines[0].endswith('】'):
		p = lines[0].index('【')
		str = lines[0][p+len('【'):-len('】')]
		return str
	else:
		str = unicode(lines[0], 'utf-8')
		p = len(str)-1
		while p >= 0 and ord(str[p]) < 0x300:
			p -= 1
		if p < len(str) -1 and str[p+1] == ')':
			p += 1
		try:
			assert p >= 0 and p < len(str) - 1
		except:
			print >> sys.stderr, 'p =', p, '  str = ', str.encode(
					'gbk', 'replace'), `str`
			raise
		str = str[:p+1]
		for i in range(len(str)):
			if not str[i] in markchars:
				break
		for c in str[:i]:
			try:
				assert c in markchars
			except:
				print >>sys.stderr,'Unexpected key field suffix'
				print >>sys.stderr, str.encode('gbk', 'replace')
				print >>sys.stderr, `c`, '(u%04X)' % (ord(c))
				raise
		str = str[i:]
		if str.find(u'(') < 0:
			try:
				assert isallcjk(str)
			except:
				print >>sys.stderr,'Contain non-CJK char'
				print >>sys.stderr, str.encode('gbk', 'replace')
				print >>sys.stderr, `lines[0]`
				print >>sys.stderr, `str`, lines[0] == unicode(
					lines[0], 'utf-8').encode('utf-8')
				raise
			return str.encode('utf-8')
		assert str.endswith(u')')
		str = str[:-1].replace(u'(', u'|', 1).replace(u'\u30fb', u'|')
		str = str.replace(u';', u'|')
		if str.startswith(u'\u2015') or str.startswith(u'\u2212'):
			str = str[1:]
		str = removedigit(str)
		try:
			assert isallcjk(str)
		except:
			print >>sys.stderr,'Contain non-CJK char'
			print >>sys.stderr, str.encode('gbk', 'replace')
			print >>sys.stderr, `lines[0]`
			print >>sys.stderr, `str`, lines[0] == unicode(
				lines[0], 'utf-8').encode('utf-8')
			raise
		str = str.replace(u'||', u'|')
		global simp
		ar = str.split(u'|')
		for c in ar[1:]:
			if len(c) > 1 or c.encode('gb2312', 'ignore'):
				continue
			if simp.has_key(c) and ar[0] not in simp[c]:
				print >>sys.stderr,'Multiple trad-simp mapping'
				print >>sys.stderr, c.encode('gbk', 'replace'),
				print >>sys.stderr, '->', simp[c][0].encode(
						'gbk', 'replace'), 'and',
				print >>sys.stderr, c.encode('gbk', 'replace'),
				print >>sys.stderr, '->', ar[0].encode('gbk',
						'replace')
				simp[c].append(ar[0])
			elif not simp.has_key(c) and c != ar[0]:
				simp[c] = [ar[0]]
		return str.encode('utf-8')

def output_entry(word, *mean):
	sys.stdout.write(word)
	sys.stdout.write('\t')
	sys.stdout.write('\\n'.join(mean))
	sys.stdout.write('\n')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s filename" % (sys.argv[0])
		print "Convert output of ebstopcode to stardict babylon text format"
		print "This version is specialized for Xxg2 Zhongri"
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
	if result is not None:
		if lastline and result[-1] != lastline:
			result.append(lastline)
		finaldic.append(result)
	f.close()
	print >> sys.stderr, 'Word count =', wordcount
	for entry in finaldic:
		output_entry(*entry)

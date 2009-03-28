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

def removedigit(str):
	result = []
	last = False
	for c in str:
		if 0x2276 <= ord(c) <= 0x277c or 0xff10 <= ord(c) <= 0xff19:
			last = True
		elif c in u',-.\u3000' and last:
				pass
		else:
			last = False
			result.append(c)
	return u''.join(result)

def isallcjk(str):
	for c in str:
		p = ord(c)
		if 0x4e00 <= p <= 0x9fc3 or 0x3400 <= p <= 0x4db5 or\
			0xf900 <= p <= 0xfad9 or 0x20000 <= p <= 0x2a6d6 or\
			0x2f800 <= p <= 0x2fa1d or p == 0x3007: # CJK characters
			pass
		elif 0xD800 <= p <= 0xDFFF: # surrogate pair for narrow python
			pass
		elif c in u'{/@}|':
			pass
		else:
			return False
	return True

simp = {}

def gettitle(lines, state):
	if lines[0].startswith('【'):
		if lines[0].endswith('】'):
			str = lines[0][len('【'):-len('】')]
		else:
			pos = lines[0].index('】')
			str = unicode(lines[0][pos+len('】'):], 'utf-8')
			for c in str:
				assert c in markchars
			str = lines[0][len('【'):pos]
		if str not in ('一二・九运动', '十・一'):
			str = str.replace('・', '|')
		else:
			str = str.replace('・', '·')
		if str.startswith('‐'):
			str = str[len('‐'):]
		return str
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
		str = str[:-1].replace(u'(', u'|').replace(u'\u30fb', u'|')
		if str.startswith(u'\u2015'):
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
					#sys.stdout.write('\n\n')
					assert result is not None
					finaldic.append(result)
					result = None
				elif laststate == keycode and (state == begcode\
						or state == endcode):
					#sys.stdout.write('\t')
					#sys.stdout.write(gettitle(titleline, 
					#	state))
					#sys.stdout.write('\n')
					#sys.stdout.write('<br>'.join(titleline))
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
				elif state in (begcode, paracode): pass
				elif state == endcode: pass
				else:
					raise 'Unknown state %04x after %04x' %(
							state, laststate)
			else:
				if lastline is not None and state != keycode:
					#sys.stdout.write(lastline)
					##sys.stdout.write('\\n')
					#sys.stdout.write('<br>')
					result.append(lastline)
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
	#sys.stdout.write('\n\n')
	if result is not None:
		finaldic.append(result)
	f.close()
	print >> sys.stderr, 'Word count =', wordcount
	for entry in finaldic:
		if entry[1].startswith('【'):
			word = unicode(entry[0], 'utf-8')
			result = []
			ch = None
			for c in word:
				if 0xD800 <= ord(c) <= 0xDBFF:
					ch = c
					continue
				elif 0xDC00 <= ord(c) <= 0xDFFF:
					c = ch + c
					ch = None
				if simp.has_key(c) and c != u'\u7947':
					print >> sys.stderr, 'Warning: traditional character %s in compound word' % c.encode('gbk', 'replace'), word.encode('gbk', 'replace'),
				else:
					result.append(c)
					continue
				if len(simp[c]) == 1:
					print >> sys.stderr, 'replace with',
					print >> sys.stderr, simp[c][0].encode(
							'gbk', 'replace'),
					result.append(simp[c][0])
					continue
				print >> sys.stderr, 'do not replace due to',
				print >> sys.stderr, 'multiple mappings:',
				for s in simp[c]:
					print >> sys.stderr, s.encode(
							'gbk', 'replace'),
				print >> sys.stderr
				result.append(c)
			newword = u''.join(result)
			if word != newword:
				result = word.split(u'|')
				for str in newword.split(u'|'):
					if str not in result:
						result.append(str)
				word = u'|'.join(result).encode('utf-8')
				print >> sys.stderr, 'done',
				print >> sys.stderr, u'|'.join(result).encode(
						'gbk', 'replace')
			else:
				word = entry[0]
		else:
			word = entry[0]
		sys.stdout.write(word)
		sys.stdout.write('\n')
		sys.stdout.write('<br>'.join(entry[1:]))
		sys.stdout.write('<br>\n\n')

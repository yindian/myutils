#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, re
try:
	import psyco
	psyco.full()
except:
	pass

stopcodestr = '=== stop-code?:'
wordcode = 0x1f41
itemcode = 0x1f09
keycode  = 0x0100
begcode = 0x0004
endcode = 0x0001
kanjisep = re.compile(u'[\u30fb;]')
delparen = re.compile(ur'\(.*?\)|\uff08\(.*?\)\uff09')

def iskana(str):
	for c in str:
		if not 0x3041 <= ord(c) <= 0x30FF:
			return False
	return True

def ishiragana(str):
	for c in str:
		if not 0x3041 <= ord(c) <= 0x30A0:
			return False
	return True

def iskatakana(str):
	for c in str:
		if not 0x30A1 <= ord(c) <= 0x30FF:
			return False
	return True

def splitkatakana(str):
	result = []
	lastiskatakana = None
	for c in str:
		if 0x30A1 <= ord(c) <= 0x30FF:
			if lastiskatakana:
				result[-1].append(c)
			else:
				result.append([c])
			lastiskatakana = True
		else:
			if lastiskatakana or lastiskatakana is None:
				result.append([c])
			else:
				result[-1].append(c)
			lastiskatakana = False
	return [u''.join(x) for x in result]

def splitkanji(str, sep):
	result = []
	lastissep = None
	for c in str:
		if c == sep:
			if lastissep:
				result[-1].append(c)
			else:
				result.append([c])
			lastissep = True
		else:
			if lastissep or lastissep is None:
				result.append([c])
			else:
				result[-1].append(c)
			lastissep = False
	return [u''.join(x) for x in result]

def vbar2eqsyn(str):
	return str

def expandsyn(str):
	p = str.find(u'\uff1d')
	q = str.find(u'\uff08')
	r = str.find(u'\uff09')
	try:
		assert p < q < r or (p == q+1 and p < r)
	except:
		print >> sys.stderr, str.encode('gbk', 'replace'), p, q, r
		raise
	return str

foreignlang = set([])
lastmidashi = None
specialcasemap = {
		u'γ —酪酸':	u'γアミノ酪酸',
		u'CS —放送':	u'CSテレビ放送',
		u'CV —':	u'CVケーブル',
		u'J —効果':	u'Jカーブ効果',
		u'—相互作用':	u'重力相互作用',
		u'—電車':	u'ちんちん電車',
		u'DNA —法':	u'DNAフィンガープリント法',
		u'T —球':	u'Tリンパ球',
		u'BB —':	u'BBレシオ',
		u'B —球':	u'Bリンパ球',
		}
def gettitle(lines, state, lineno):
	#assert state == begcode
	global lastmidashi
	if state != begcode:
		print >> sys.stderr, 'Warning: empty mean for %s' % (
			unicode(lines[0], 'utf-8').encode('gbk', 'replace'))
	assert len(lines) == 2
	assert lines[1] == ''
	#return lines[0].strip()
	line = unicode(lines[0].strip(), 'utf-8')
	kana = kanjis = None
	if line.find(u'\u3010') >= 0:
		assert line.count(u'\u3010') == line.count(u'\u3011')
		p = line.find(u'\u3010')
		q = line.find(u'\u3011')
		assert p < q
		ar = line[:p].strip().split()
		if ar[-1][-1] == u']':
			assert ar[-1][0] == u'['
		kanaraw = ar[0]
		kana = kanaraw.replace(u'\u30fb', u'').replace(u'-', u''
				).replace(u'\u2218', u'')
		assert iskana(kana)
		kanjis = [x.strip() for x in line[p+1:q].split(u'\u30fb')]
	elif line.find(u'\u3016') >= 0:
		assert line.count(u'\u3016') == line.count(u'\u3017') == 1
		p = line.find(u'\u3016')
		q = line.find(u'\u3017')
		assert p < q
		ar = line[:p].strip().split()
		if ar[-1][-1] == u']':
			assert ar[-1][0] == u'['
		kanaraw = ar[0]
		kana = kanaraw.replace(u'\u30fb', u'').replace(u'-', u''
				).replace(u'\u2218', u'')
		assert iskana(kana) or lineno >= 1879260
		if not iskatakana(kana):
			kana = kana.replace(u'\u307a', u'\u30da').replace(
					u'\u3078', u'\u30d8').replace(
							u'\u3079', u'\u30d9')
		if lineno < 1879260 and not iskatakana(kana):
			kana = kanaraw.replace(u'\u30fb', u'').replace(u'-', u''
					).replace(u'\u2218', u'')
			ar = kanaraw.split(u'-')
			if len(ar) == 1:
				assert kanaraw.find(u'\u3068') > 0
				ar = kanaraw.split(u'\u3068')
			try:
				for s in ar:
					assert iskatakana(s) or ishiragana(s)
			except:
				print >> sys.stderr, 'Mixed kana: %s' % (
					unicode(lines[0], 'utf-8'
						).encode('gbk',
							'replace'))
		else:
			kana = kana.replace(u',', u'|')
		kanjis = [x.strip() for x in kanjisep.split(line[p+1:q])]
		if len(kanjis[0]) > 2 and 0xA000 > ord(kanjis[0][0]) > 0x3000 \
				and ord(kanjis[0][1]) < 0x3000:
			kanji = kanjis[0]
			if kanji[0] not in foreignlang:
				print >> sys.stderr, 'Foreign language encountered:', kanji[0].encode('gbk', 'replace')
				foreignlang.add(kanji[0])
			kanji = kanji[1:].lstrip()
			kanjis[0] = kanji
		elif kanjis[0][0] == u'\uff08':
			p = kanjis[0].find(u'\uff09')
			assert p > 0
			kanjis[0] = kanjis[0][p+1:].strip()
		for i in range(len(kanjis)):
			if kanjis[i][0] == u'(':
				kanjis[i] = kanjis[i][kanjis[i].index(u')')+1:]
				kanjis[i] = kanjis[i].strip()
		try:
			assert u''.join(kanjis).find(u'(') < 0
			assert u''.join(kanjis).find(u')') < 0
		except:
			print >> sys.stderr, u''.join(kanjis).encode('gbk',
					'replace')
			raise
		#TODO
	else:
		ar = delparen.sub(u'', line).strip().split()
		if ar[-1][-1] == u']':
			assert ar[-1][0] == u'['
		kanaraw = ar[0]
		kana = kanaraw.replace(u'\u30fb', u'').replace(u'-', u''
				).replace(u'\u2218', u'')
		if iskana(kana):
			pass
		else:
			try:
				assert len(ar) == 1 or (len(ar) == 2 and
						ar[1][0] == u'\uff08' and
						ar[1][-1] == u'\uff09')
			except:
				print >> sys.stderr, ar
				raise
			if kana.startswith(u'\u2014\u2014'):
				kana = vbar2eqsyn(lastmidashi) + kana[2:]
			else:
				#print >> sys.stderr, 'Not kana:', kana.encode(
				#		'gbk', 'replace')
				assert kana.find(u'\u2014') < 0
			if kana.find(u'\uff1d') >= 0:
				kana = expandsyn(kana)
		return kana.encode('utf-8')
	linenew = line[q+1:]
	if line[p+1:q].find(u'\u2014') >= 0:
		assert line[q+1:].find(u'\u3010') < 0
		assert line[q+1:].find(u'\u3016') < 0
		#assert line[p+1:q].find(u'\u2014\u2014') < 0
		ar = splitkatakana(kana)
		if len(ar) == 1:
			ar = kanaraw.split(u'-')
		assert len(ar) > 1
		for k in range(len(kanjis)):
			kanji = kanjis[k]
			assert kanji.count(u'(') < 2
			assert kanji.count(u')') == kanji.count(u'(')
			if kanji.find(u')') >= 0:
				p = kanji.find(u'(')
				q = kanji.find(u')')
				assert p < q
				if kanji.find(u'\u2014') < 0:
					kanji = '%s%s|%s%s%s' % (kanji[:p],
							kanji[q+1:], kanji[:p],
							kanji[p+1:q], kanji[
								q+1:])
					kanjis[k] = kanji
			if kanji.find(u'\u2014') < 0: continue
			br = splitkanji(kanji, u'\u2014')
			try:
				assert len(ar) == len(br)
				for i in range(len(ar)):
					if br[i] == u'\u2014':
						assert iskatakana(ar[i])
						br[i] = ar[i]
				kanji = u''.join(br)
			except:
				if specialcasemap.has_key(kanji):
					kanji = specialcasemap[kanji]
				else:
					print >> sys.stderr, 'Error for %s' % (
						unicode(lines[0], 'utf-8'
							).encode('gbk',
								'replace'))
				#TODO
				#continue
			if kanji.find(u')') >= 0:
				p = kanji.find(u'(')
				q = kanji.find(u')')
				assert p < q
				kanji = '%s%s|%s%s%s' % (kanji[:p],
						kanji[q+1:], kanji[:p],
						kanji[p+1:q], kanji[
							q+1:])
			kanjis[k] = kanji
	line = linenew
	while line.find(u'\u3010') >= 0:
		p = line.find(u'\u3010')
		q = line.find(u'\u3011')
		assert p < q
		kanjis.extend([x.strip()
			for x in line[p+1:q].split(u'\u30fb')])
		line = line[q+1:]
	while line.find(u'\u3016') >= 0:
		p = line.find(u'\u3016')
		q = line.find(u'\u3017')
		assert p < q
		kanjis.extend([x.strip()
			for x in line[p+1:q].split(u'\u30fb')])
		line = line[q+1:]
	lastmidashi = (kana + u'|' + u'|'.join(kanjis))
	return lastmidashi.encode('utf-8')

def output_entry(word, origtitle, *mean):
	sys.stdout.write(word)
	sys.stdout.write('\t')
	sys.stdout.write(origtitle)
	sys.stdout.write('\\n')
	sys.stdout.write('\\n'.join(mean))
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
	lineno = 0
	for line in f:
		lineno += 1
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
					try:
						result = [gettitle(titleline,
							state, lineno)]
					except:
						print >> sys.stderr, 'Line %d'%(
								lineno,)
						raise
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

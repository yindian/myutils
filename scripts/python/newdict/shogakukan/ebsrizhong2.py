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

foreignlang = set([])
specialcasemap = {
		u'ID—': u'IDカード',
		u'I—': u'Iビーム',
		u'EE—': u'EEカメラ',
		u'E—': u'Eメール',
		u'Web—': u'Webページ',
		u'—C': u'ウルトラC',
		u'A—': u'Aクラス',
		u'AV—': u'AVビデオ',
		u'H．B．—': u'H．B．プロセス',
		u'H—法': u'Hアイアン法',
		u'F—': u'Fナンバー',
		u'OF—': u'OFケーブル',
		u'買い—': u'買いオペ（レーション）',
		u'空中—': u'空中ぶらんこ',
		u'—酸': u'くえん酸',
		u'CT—': u'CTスキャナー',
		u'GB—': u'GBコード',
		u'G—': u'Gマーク',
		u'G—': u'Gパン',
		u'G—': u'Gメン',
		u'J—': u'Jリーグ',
		u'新—': u'新モス（リン）',
		u'第三—': u'第三インター（ナショナル）',
		u'第二—': u'第二インター（ナショナル）',
		u'—Q{?w=e132}': u'ダイヤルQ{?w=e132}',
		u'T—': u'Tシャツ',
		u'T—': u'Tバック',
		u'生—': u'生コン（クリート）',
		u'PS—': u'PSコンクリート',
		u'Big5—': u'Big5コード',
		u'—焼': u'もんじゃ焼',
		}

def gettitle(lines, state):
	assert state == begcode
	assert len(lines) == 2
	assert lines[1] == ''
	#return lines[0].strip()
	line = unicode(lines[0].strip(), 'utf-8')
	if line.find(u'\uff0a') >= 0:
		assert line[0] == u'\uff0a'
		line = line[1:]
	if line.find(u'\u3010') >= 0:
		assert line[-1] == u'\u3011'
		p = line.find(u'\u3010')
		kana = line[:p]
		kanji = line[p+1:-1]
	else:
		kana = line
		kanji = ''
	if kana.find(u'\u30fb') >= 0:
		#if not iskatakana(kana):
		#	print >> sys.stderr, 'With middle dot:', kana.encode('gbk', 'replace')
		kana = kana.replace(u'\u30fb', u'')
	if kanji and iskatakana(kana) and ord(kanji[0]) > 0x3000 and (ord(kanji[-1]) < 0x3000 or ord(kanji[-1]) > 0xff00):
		assert ord(kanji[1]) < 0x3000
		assert kanji.find(u'\u2014') < 0
		if kanji[0] not in foreignlang:
			print >> sys.stderr, 'Foreign language encountered:', kanji[0].encode('gbk', 'replace')
			foreignlang.add(kanji[0])
		kanji = kanji[1:]
	if kanji.find(u'\u2014') >= 0:
		assert kanji.find(u'\u2014\u2014') < 0
		ar = splitkatakana(kana)
		try:
			if len(ar) > 1:
				br = splitkanji(kanji, u'\u2014')
				assert len(ar) == len(br)
				for i in range(len(ar)):
					if br[i] == u'\u2014':
						assert iskatakana(ar[i])
						br[i] = ar[i]
				#print >> sys.stderr,'Info: convert %s(%s) to '\
				#		% (kana.encode('gbk', 'replace')
				#				, kanji.encode(
				#					'gbk',
				#					'replace')),
				kanji = u''.join(br)
				#print >> sys.stderr, kanji.encode('gbk', 
				#		'replace')
			else:
				assert len(ar) > 1
		except AssertionError:
			if specialcasemap.has_key(kanji):
				kanji = specialcasemap[kanji]
			else:
				print >> sys.stderr, 'Unable to split katakana:', kana.encode('gbk', 'replace')
	if kanji:
		return (u'%s|%s' % (kana, kanji)).encode('utf-8')
	else:
		return kana.encode('utf-8')

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
	lineno = 0
	try:
		f = open(sys.argv[1], 'r')
		state = laststate = keycode
		chgflag = False
		lastline = None
		titleline = []
		wordcount = 0
		finaldic = []
		result = None
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
	except:
		print >> sys.stderr, 'Error on line %d' % (lineno,)
		raise
	print >> sys.stderr, 'Word count =', wordcount
	for entry in finaldic:
		output_entry(*entry)

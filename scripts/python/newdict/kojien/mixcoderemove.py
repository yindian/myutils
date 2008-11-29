#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string

def iskana(char):
	#return 0x3040 < ord(char) < 0x30A0
	return 0x3000 < ord(char) < 0x3100 #0x30A0

def validsplit(str, pos):
	if pos == 0:
		return False
	a = str[:pos]
	b = str[pos:]
	assert iskana(b[-1])
	if iskana(a[-1]):
		if len(a) > 1 and iskana(a[-2]):
			return a[-1] == b[-1] and a[-2] == b[-2]
		else:
			return a[-1] == b[-1]
	else:
		if iskana(a[0]):
			return a[0] == b[0]
		else:
			print >> sys.stderr, 'Uncertain: %s | %s' % (
					a.encode('gbk'), b.encode('gbk'))
			return True

mixcode = u'\u25cb'.encode('utf-8')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "This version is specialized for Kojien 6"
		sys.exit(0)
	f = open(sys.argv[1], 'r')
	state = 0
	lastline = None
	for line in f:
		if line.startswith(mixcode):
			if state == 0:
				lastline = line[:-1]
				state = 1
			elif state == 1:
				state = 2
			else:
				raise
		if state == 0:
			sys.stdout.write(line)
		elif state == 2:
			assert line.startswith(lastline)
			lastline = unicode(lastline, 'utf-8')
			lastline = lastline[1:]
			line = unicode(line, 'utf-8')
			word = line[line.index(u'b655>')+5:-5]
			#print >> sys.stderr, word.encode('gbk', 'replace')
			if word.find(u'\u3010') < 0:
				kana = word
				kanji = ''
			else:
				kana = word[:word.find(u'\u3010')]
				kanji = word[word.find(u'\u3010')+1:-1]
				assert word[-1] == u'\u3011'
			kana = kana.replace(u'\u2010', u'')
			if kana.find(u'\u30fb') >= 0:
				kana = kana[:kana.find(u'\u30fb')]
			elif kana[-1] == u'\u308b':
				kana = kana[:-1]
			if kanji != '':
				i = len(lastline)
				while i > 0 and iskana(lastline[i-1]):
					i -= 1
				pos = lastline.find(kana, i)
				found = False
				while pos >= 0:
					if validsplit(lastline, pos):
						lastline = lastline[:pos] + \
								u'|' + \
								lastline[pos:]
						found = True
						break
					pos = lastline.find(kana, pos+1)
				if not found:
					print >> sys.stderr, 'Not found %s' % (
							lastline.encode('gbk')),
					print >> sys.stderr, '(%s [%s])' % (
							kana.encode('gbk',
								'replace'),
							kanji.encode('gbk',
								'replace')),
			lastline = lastline.encode('utf-8')
			line = line.encode('utf-8')
			sys.stdout.write(lastline)
			sys.stdout.write('\n')
			sys.stdout.write(line)
			state = 0
	f.close()

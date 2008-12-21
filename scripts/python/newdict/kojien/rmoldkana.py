#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path, operator

def showhelp():
	print "Usage: %s tabfile [list]" % (os.path.basename(sys.argv[0]))
	print "Remove the old kana orthography from word"
	print "Lines beginning with # or ? in list file are not removed"
	sys.exit(0)

def ishiragana(ch):
	return 0x3040 < ord(ch) < 0x3098

def iskatakana(ch):
	return 0x3098 < ord(ch) < 0x3100

def isleader(ch):
	return 0x2024 <= ord(ch) <= 0x2026

def iskatakanaorleader(ch):
	return 0x3098 < ord(ch) < 0x3100 or 0x2024 <= ord(ch) <= 0x2026

def kanasplit(str):
	str = unicode(str, 'utf-8')
	try:
		assert ishiragana(str[0])
		assert iskatakanaorleader(str[-1])
		pos = len(str)
		while pos > 0 and iskatakanaorleader(str[pos-1]):
			pos -= 1
		for i in range(pos):
			if not ishiragana(str[i]):
				return (True, '#'+str, str[:pos])
		for i in range(pos, len(str)):
			if isleader(str[i]):
				return (True, '?'+str, str[:pos])
		s = str[pos:]
		if reduce(operator.add, map(s.count, 
			u'クグハヒフヘホヰヱヲヂヅ')) > 0:
			return (True, str, str[:pos])
		return (True, '#'+str, str[:pos])
	except:
		return (False,)

if __name__ == '__main__':
	if not len(sys.argv) in (2, 3):
		showhelp()
	if len(sys.argv) == 2:
		f = open(sys.argv[1], 'r')
		for line in f:
			pos = line.index('\t')
			line = line[:pos]
			if line.find('|') >= 0:
				continue
			ret = kanasplit(line)
			if ret[0]:
				ret = map(lambda s: s.encode('utf-8'), ret[1:])
				print '%s\t%s' % tuple(ret)
		f.close()
	else:
		f = open(sys.argv[2], 'r')
		oldlist = {}
		for line in f:
			if line[0] in '#?':
				continue
			line = line[:-1].split('\t')
			assert len(line) == 2
			oldlist[line[0]] = line[1]
		f.close()
		f = open(sys.argv[1], 'r')
		for line in f:
			line = line[:-1].split('\t')
			if oldlist.has_key(line[0]):
				line[0] = oldlist[line[0]]
			print '%s\t%s' % tuple(line)
		f.close()

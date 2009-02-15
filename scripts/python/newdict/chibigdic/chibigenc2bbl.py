#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string
import fileinput

def parsemarkup(str):
	if str.find('[[') > 0:
		str = str.replace('[[', '<span foreground="blue">').replace(
				']]', '</span>')
	str = str.split('\\')
	if len(str) == 1:
		return str[0]
	result = [str[0]]
	empty = 0
	for s in str[1:]:
		if s.startswith('I{'):
			result.append('<big>')
			result.append(s[2:s.find('}')])
			result.append('</big>')
			result.append(s[s.find('}')+1:])
		elif s.startswith('i{'):
			result.append('<b>')
			result.append(s[2:s.find('}')])
			result.append('</b>')
			result.append(s[s.find('}')+1:])
		elif s.startswith('u{'):
			result.append('<u>')
			result.append(s[2:s.find('}')])
			result.append('</u>')
			result.append(s[s.find('}')+1:])
		elif s.startswith('a{'):
			result.append('<u><i>')
			result.append(s[2:s.find('}')])
			result.append('</i></u>')
			result.append(s[s.find('}')+1:])
		elif s.startswith('be{}'):
			result.append('  ')
			result.append(s[4:])
		elif s.startswith('ee{}'):
			result.append(s[4:])
		elif s == '':
			assert empty <= 2
			empty += 1
			#print >> sys.stderr, 'Warning: empty markup', 
			#result.append('\\')
		else:
			if s[0] == '[' and empty == 1:
				result.append('<span foreground="red">')
				result.append(s)
			elif s[0] == ']' and empty == 2:
				result.append(']')
				result.append('</span>')
				result.append(s[1:])
			elif s[0] == ']' and empty == 0:
				result.append(s)
			else:
				raise 'Unknown markup'
			empty = 0
			#print >> sys.stderr, 'Warning: unknown markup', 
			#print >> sys.stderr, unicode(s, 'utf-8').encode('gbk', 
			#	'replace')
			#result.append(s)
			#raise 'Unknown markup'
	return ''.join(result)

state = newstate = 0
word = mean = None
lastword = lastmean = None

sys.stdout = open('chibigenc.txt', 'w')
for line in fileinput.input():
	try:
		assert line[-1] == '\n'
		line = line[:-1]
		if not line:
			continue # ignore empty lines
		if line == '----------':
			newstate = 1
		elif line == '==========':
			newstate = 2
		else:
			newstate = 0
		if (state, newstate) == (0, 0):
			assert not word
			word = line
		elif (state, newstate) == (0, 1):
			mean = []
			state = 1
		elif (state, newstate) == (1, 0):
			line = line.replace('&', '&amp;').replace('<', 
				'&lt;').replace('>', '&gt;').replace("'", 
					'&apos;').replace('"', '&quot;')
			line = parsemarkup(line)
			mean.append(line)
		elif (state, newstate) == (1, 2):
			assert word and mean
			if word == lastword and ''.join(mean) == lastmean:
				print >> sys.stderr, 'Warning: duplicate word',
				print >> sys.stderr, unicode(word, 'utf-8'
						).encode('gbk', 'replace')
			else:
				print word
				print '<br>'.join(mean)
				print
			state = 0
			lastword = word
			lastmean = ''.join(mean)
			word = mean = None
		else:
			raise (state, newstate)
	except:
		print >> sys.stderr, 'Error on line:',
		print >> sys.stderr, unicode(line, 'utf-8').encode('gbk', 
				'replace')
		raise
sys.stdout.close()

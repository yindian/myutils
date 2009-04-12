#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path, codecs

def showhelp():
	print "Usage: %s [-r] txtfile" % (os.path.basename(sys.argv[0]))
	print "Convert mdict export file to babylon-style or vice versa."
	sys.exit(0)

if __name__ == '__main__':
	if not len(sys.argv) in (2, 3):
		showhelp()
	if len(sys.argv) == 2:
		#f = codecs.open(sys.argv[1], 'rb', 'utf-16le')
		f = open(sys.argv[1], 'rb')
		lines = []
		firstline = True
		for line in f:
			if firstline:
				if line.startswith('\xff\xfe'): line = line[2:]
				firstline = False
				lines = [None]
			#print >> sys.stderr, line.encode('gbk', 'replace'), `line`
			if not line.startswith('\0<\0/\0>\0'):
				lines.append(line)
			else:
				if lines == ['\0']:
					break
				if lines[0] is None: # first line
					del lines[0]
				elif lines[0][0] == '\0':
					lines[0] = lines[0][1:]
				line = ''.join(lines)
				if line[-1] == '\n':
					line = line + '\0'
				line = unicode(line, 'utf-16le')
				if line.find(u'\r\n') >= 0:
					lines = line.split(u'\r\n')
				else:
					lines = line.split(u'\n')
				print lines[0].encode('utf-8')
				#if lines[1].startswith(u'<br>'):
				#	lines[1] = lines[1][4:]
				print u''.join(lines[1:]).encode('utf-8')
				print
				lines = []
		if lines and lines != ['\0']:
			print lines[0].encode('utf-8')
			#if lines[1].startswith(u'<br>'):
			#	lines[1] = lines[1][4:]
			print u''.join(lines[1:]).encode('utf-8')
			print
			lines = []
		f.close()
	elif sys.argv[1] != '-r':
		showhelp()
	else:
		f = open(sys.argv[2], 'r')
		if sys.platform == 'win32':
			import os, msvcrt
			msvcrt.setmode(sys.stdout.fileno(  ), os.O_BINARY)
		sys.stdout.write('\xff\xfe')
		state = 0
		result = None
		lineno = 0
		for line in f:
			lineno += 1
			if line[-1] == u'\n':
				line = line[:-1]
			line = unicode(line, 'utf-8')
			if not line and state == 1:
				state = 0
				if result:
					if len(result) > 2:
						if result[2].startswith('\r\n'):
							result[2]= result[2][2:]
						result.append(u'\r\n')
					result.append(u'</>\r\n')
					result = map(lambda s: s.encode(
						'utf-16le'), result)
					sys.stdout.write(''.join(result))
					result = None
				else:
					print >> sys.stderr, 'Empty line',\
							lineno, 'ignored'
			elif not line:
				print >> sys.stderr, 'Ignore empty line', lineno
			elif state == 0:
				result = [line, u'\r\n']
				state = 1
			else:
				result.append(line.replace('<br>', '\r\n<br>'))
		if result:
			if len(result) > 2:
				if result[2].startswith('\r\n'):
					result[2]= result[2][2:]
				result.append(u'\r\n')
			result.append(u'</>\r\n')
			result = map(lambda s: s.encode('utf-16le'), result)
			sys.stdout.write(''.join(result))
		f.close()

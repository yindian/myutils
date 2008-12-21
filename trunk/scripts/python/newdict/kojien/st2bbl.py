#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, string, os.path

def showhelp():
	print "Usage: %s [-r] txtfile" % (os.path.basename(sys.argv[0]))
	print "Convert stardict tab file to babylon-style or vice versa."
	sys.exit(0)

if __name__ == '__main__':
	if not len(sys.argv) in (2, 3):
		showhelp()
	if len(sys.argv) == 2:
		f = open(sys.argv[1], 'r')
		for line in f:
			pos = line.index('\t')
			print line[:pos]
			print line[pos+1:].replace('\\n', '<br>')
		f.close()
	elif sys.argv[1] != '-r':
		showhelp()
	else:
		f = open(sys.argv[2], 'r')
		state = 0
		result = None
		for line in f:
			line = line[:-1]
			if not line:
				state = 0
				if result:
					print ''.join(result)
					result = None
				else:
					print >> sys.stderr, 'Ignore empty line'
			elif state == 0:
				result = [line, '\t']
				state = 1
			else:
				result.append(line.replace('<br>', '\\n'))
		if result:
			print ''.join(result)
		f.close()

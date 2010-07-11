#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, re, glob
import pdb, traceback

S_INIT = 0
S_BODY = 1
S_MEAN = 2
_statedata = {}
_statedata2 = []

def output(str, newline=True):
	return
	if newline:
		print str
	else:
		print str,

_wordmap = {
		'six': 'one',
		'ten': 'two',
		'five': 'four',
		'nine': 'five',
		'three': 'eight',
		'seven': 'three',
		'eight': 'seven',
		}
def textconv(str, domap=False, wordmap=_wordmap):
	if domap:
		ar = str.split()
		for i in xrange(len(ar)):
			if wordmap.has_key(ar[i]):
				ar[i] = wordmap[ar[i]]
		str = ' '.join(ar)
	return str.decode('utf-8').encode('sjis', 'xmlcharrefreplace')

def getattr(str):
	result = []
	p = 0
	while p < len(str):
		while p < len(str) and str[p].isspace():
			p += 1
		i = p
		while i < len(str) and str[i] != '=' and not str[i].isspace():
			i += 1
		result.append([str[p:i], None])
		if i < len(str) and str[i] == '=':
			i += 1
			if i < len(str) and str[i] in ''''"''':
				q = str.index(str[i], i+1)
				i += 1
				p = q+1
			else:
				q = i
				while q < len(str) and not str[q].isspace():
					q += 1
				p = q
			result[-1][1] = str[i:q]
		else:
			p = i
	return dict(result)

def parseline(line, state, d=_statedata, dd=_statedata2):
	if line.endswith('\n'):
		line = line[:-1]
	if state == S_INIT:
		if line.startswith('<body'):
			state = S_BODY
			dd.append(d.copy())
			d.clear()
			d['stack'] = []
			output('<dl>')
		return state
	elif state == S_BODY or state == S_MEAN:
		if line.find('</body>') >= 0:
			state = S_INIT
			output('</dl>')
			return state
	ar = line.split('<')
	if ar[0].strip():
		output(textconv(ar[0]), False)
	for i in xrange(1, len(ar)):
		p = ar[i].find('>')
		br = ar[i][:p].split(' ', 1)
		if ar[i].startswith('/'):
			try:
				assert d['stack'][-1][0] == br[0][1:]
				del d['stack'][-1]
			except:
				if br[0] != '/a':
					raise
		else:
			if br[0] not in ('img', 'br', 'pt'):
				d['stack'].append((br[0],
					len(br)>1 and br[1] or None))
			if br[0] == 'span' and len(br) > 1:
				attr = getattr(br[1])
				if attr.has_key('class'):
					if attr['class'] == 'oa_genie_h':
						pass
				
	return state

assert __name__ == '__main__'

if len(sys.argv) < 2:
	print 'Usage: %s data*.txt' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

flist = glob.glob(sys.argv[1])
flist.sort()

state = S_INIT
for fname in flist:
	f = open(fname, 'r')
	lineno = 0
	try:
		for line in f:
			lineno += 1
			state = parseline(line, state)
			#if lineno > 1000:
			#	break
	except:
		print >> sys.stderr, 'Error processing %s:%d' % (fname, lineno)
		traceback.print_exc()
		pdb.set_trace()
	f.close()

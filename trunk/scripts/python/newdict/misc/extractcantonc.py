#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob
import libxml2dom

whatfile = 'temp/*.out'
outfile = 'e.out'

def splitWord(str):
	p = str.find('[')
	if p < 0:
		return [str]
	q = str.find(']')
	if q < 0:
		raise 'Square brackets not match'
	i = p-1
	while i > 0 and ord(str[i]) < 256:
		i -= 1
	# now str[i:p] is the word 
	ar = filter(None, str[p+1:q].split(u'\u3001'))
	for s in ar:
		if len(s) <> len(ar[0]):
			raise 'Synonym length mismatch'
	result = []
	if len(ar) > 0 and len(ar[0]) > 1:
		i -= len(ar[0])-1
		if i < 0:
			i = 0
	ar = [str[i:p]] + ar
	for res in splitWord(str[q+1:]):
		for s in ar:
			result += [str[:i] + s + res]
	return result

def parseTransSyn(str):
	for i in range(len(str)):
		if ord(str[i]) >= 256:
			break
	trans = str[:i].strip()
	result = ''
	#result = trans
	#if i < len(str):
	#	result += '|'
	word = str[i:]
	p = word.find('[')
	if p < 0:
		result += word.strip()
	else:
		result += '|'.join(splitWord(word.strip()))
	result += '\n' + str + '<br>'
	return result

filelist = glob.glob(whatfile)
filenum = len(filelist)
num = 0
errorfiles = []
result = []
for filename in filelist:
	num += 1
	print >> sys.stderr, filename, num, 'of', filenum
	try:
		fp = open(filename, 'r')
		doc = libxml2dom.parseString(fp.read(), html=1,
				htmlencoding='utf-8')
		fp.close()
		tables = doc.getElementsByTagName("table")
		tables = tables[1:]
		for tab in tables:
			tds = tab.getElementsByTagName("td")
			if len(tds) <> 6:
				print >> sys.stderr, 'td num != 6'
				raise 'TD num != 6'
			str = parseTransSyn(tds[0].textContent)
			for td in tds[1:]:
				str += td.textContent + '<br>'
			str = str[:-4] + '\n'
			#print str.encode('latin-1')
			#print str.encode('utf-8')
			if not str in result:
				result += [str]
			#print str.encode('cp936', 'ignore')
	except:
		print >> sys.stderr, 'error occured'
		errorfiles += [filename]
		raise
		continue
if errorfiles:
	print >> sys.stderr, 'Error files:', '\n'.join(errorfiles)
fp = open(outfile, 'w')
for str in result:
	print >> fp, str.encode('utf-8')
fp.close()

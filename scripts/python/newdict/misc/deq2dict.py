#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, struct, re
if True:
	try:
		import psyco
		psyco.full()
	except:
		pass
else:
	import pdb
try:
	import json
except:
	import simplejson as json

def bformat(word, str):
	result = []
	p = 0
	while p < len(str):
		l = ord(str[p]) + 1
		if l > 1:
			result.append(str[p+1:p+l])
		p += l
	assert p == len(str)
	return '\n'.join(result)

xmltag = re.compile(r'<[^>]*>')
_htmlampquotemap = {
		'lt':	'<',
		'gt':	'>',
		'amp':	'&',
		'quot': '"',
		'apos': "'",
		}
def unhtml(str, quotemap=_htmlampquotemap):
	if type(str) == type(u''):
		mychr = unichr
	else:
		mychr = chr
	ar = str.split('&')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.find(';')
		if p < 1:
			result.append('&')
			result.append(s)
		else:
			if s[0] == '#':
				num = s[1:p]
				try:
					num = int(num)
				except:
					assert num[0].lower() == 'x'
					num = int(num[1:], 16)
				result.append(mychr(num))
			else:
				result.append(quotemap[s[:p]])
			result.append(s[p+1:])
	return ''.join(result)

_mykey = [
		('ph' + 'o', ),
		('de' + 's', 'p', 'd'),
		('se' + 'n', 'p', 's'),
		('mo' + 'r', 'c', 'm'),
		('sy' + 'n', 'p', 'c'),
		('an' + 't', 'p', 'c'),
		('st' + 'em', ),
		('ph' + '', 'phs', 'phd'),
		]

def _mytransform(dd, kk):
	assert type(dd[kk]) == type([])
	if kk == 's':
		result = []
		for d in dd[kk]:
			assert type(d) == type({})
			assert len(d) == 2
			result.extend(['', d['es'], d['cs']])
		result.append('')
		return '\n'.join(result)
	elif kk == 'c':
		return ', '.join(dd[kk])
	else:
		raise Exception('Unknown key ' + kk)

def fformat(word, str, mykey=_mykey, f=_mytransform):
	d = json.loads(str)
	assert len(d) == 1
	assert len(d['local']) == 1
	d = d['local'][0]
	result = []
	try:
		assert word == unhtml(d['word']).encode('utf-8')
	except:
		#print >> sys.stderr, `word`, '!=',
		#print >> sys.stderr, `unhtml(d['word']).encode('utf-8')`
		result.append('=> ')
		result.append(d['word'])
		result.append('\n')
	keyset = set(d.keys())
	keyset.remove('word')
	try:
		for key in mykey:
			if d.has_key(key[0]):
				dds = d[key[0]]
				if len(key) > 1:
					for dd in dds:
						if type(dd) == type(u''):
							result.append(dd)
							result.append('\n')
							continue
						assert len(dd) < len(key)
						if key[0][:2] == 'sy':
							result.append(u'同义: ')
						elif key[0][:2] == 'an':
							result.append(u'反义: ')
						elif key[0][:2] == 'ph':
							result.append(u'短语: ')
						for kk in key[1:]:
							if not dd.has_key(kk):
								continue
							if type(dd[kk]) != type(
									u''):
								dd[kk]=f(dd,kk)
							result.append(dd[kk])
							result.append(' ')
							if kk == key[-1]:
								del result[-1]
						result.append('\n')
				else:
					if key[0][:2] == 'ph':
						assert len(dds) == 1
						result.append('[')
						result.append(dds[0])
						result.append(']')
					#elif key[0][:2] == 'de':
					#	assert len(dds) == 1
					#	result.append(dds[0])
					elif key[0][:2] == 'st':
						pass
					else:
						raise Exception('Bad ' + key)
				keyset.remove(key[0])
				result.append('\n')
		if keyset:
			raise Exception('Unknown key' + `keyset`)
	except:
		print >> sys.stderr, d
		raise
	return unhtml(xmltag.sub(u'',u''.join(result)).rstrip()).encode('utf-8')

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s filename.?dic" % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'rb')
magic = f.read(4)
if magic == '\xd2' + chr(235) + '\x27' + chr(166):
	f.read(16)
	header = f.read(16)
	formatbody = bformat
elif magic == '\x7a' + chr(242) + '\x92' + chr(223):
	f.read(18)
	header = f.read(16)
	formatbody = fformat
else:
	print >> sys.stderr, 'Unrecognized file format'
	f.close()
	sys.exit(1)
idxoffset, idxlen, bodyoffset, bodylen = struct.unpack('<4L', header)

f.seek(idxoffset)
rawindex = f.read(idxlen)
indexlist = re.findall('.*?\0.{8}', rawindex, re.S)
del rawindex

print >> sys.stderr, 'Word count:', len(indexlist)
for item in indexlist:
	p = item.index('\0')
	word = item[:p]
	offset, length = struct.unpack('<LL', item[p+1:])
	f.seek(bodyoffset + offset)
	body = f.read(length)
	print '%s\t%s' % (word, formatbody(word, body).replace('\\\n',
		r'\\n').replace('\n', r'\n'))
f.close()

print >> sys.stderr, 'Done.'

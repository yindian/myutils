#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, re
import pdb

def gbk2uni(s):
	if s.find('\t') < 0:
		us = s.replace('\x80', '\xa2\xe3').decode('gb18030')
		s = us.encode('utf-8')
	else:
		ar = [s[:s.index('\t')]] + s[s.index('\t')+1:].split('\\n')
		for i in xrange(len(ar)):
			if ar[i].startswith('[') and ar[i].endswith(']'):
				pass
			else:
				ar[i] = ar[i].replace('\x80', '\xa2\xe3'
						).decode('gb18030').encode(
								'utf-8')
		s = ar[0] + '\t' + '\\n'.join(ar[1:])
	return s
def seemsgmx(s):
	for i in xrange(32):
		if chr(i) in s:
			return True
	try:
		s.decode('utf-8')
		unifail = False
	except:
		unifail = True
	try:
		s.replace('\x80', '\xa2\xe3').decode('gb18030')
		gbkfail = False
	except:
		gbkfail = True
	if unifail and gbkfail:
		return True
	if unifail and not gbkfail:
		if len(filter(lambda c: ord(c) > 0xA0, s)) < len(s) / 2:
			return True
	return False
gmx = u'''\
 ɪɛæɑ ɔ    θ  ʊʌəˌɜɚɝṃṇḷ…ŋɒ ðʃʒˌ\
 !"#$%&ˈ（）*+，-．/0123456789ː；<=>?\
@ABCDEFGHIJKLMNOPQʀＳTＵVWXYZ[\]^_\
`abcdefɡhijklmnopqrstuvwxyz{|}̃ \
€ ‚ƒ„…†‡ˆ‰Š‹Œ    ‘’“”•–—˜™š›œ  Ÿ\
 ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶•¸¹º»¼½¾¿\
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØǜǘǚǖüÞß\
àáǎãāåæçèéěēìíǐīðñòóǒõō÷øùúǔūýþÿ'''
assert len(gmx) == 256
ampquote=lambda s:s.replace('&', '&amp;').replace('<', '&lt;').replace('>',
		'&gt;').replace("'", '&apos;').replace('"', '&quot;')
ampunquote=lambda s:s.replace('&quot;', '"').replace('&apos;', "'").replace(
		'&gt;'  , '>').replace('&lt;'  , '<').replace('&amp;' , '&')

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s tabfile.txt' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'rb')
lineno = 0
line = f.readline()
if line.startswith('\t'):
	description = re.sub(r'//STE.*?//', '', gbk2uni(line[1:-1])).replace(
			'\\n', '\n')
	lineno = 1
else:
	f.seek(0)
	description = None
print '''\
<?xml version="1.0" encoding="UTF-8" ?>
<xdxf lang_from="ENG" lang_to="ENG" format="visual">
<full_name>%s</full_name>''' % (os.path.basename(sys.argv[1]),)

if description:
	print '<description>%s</description>' % (description,)

removeemptycolortag = re.compile(r'<c[^>]*></c>')
kssubscript = re.compile(r'&-\{([^\}]*)\}')
kssubscript2 = re.compile(r'&amp;-\{([^\}]*)\}')
for line in f:
	lineno += 1
	assert line[-1] == '\n'
	line = line[:-1]
	if not line:
		continue
	if line[-1] == '\r':
		line = line[:-1]
	try:
		word, mean = gbk2uni(line).split('\t', 1)
	except:
		print >> sys.stderr, 'Decode error on line', lineno
		print >> sys.stderr, line
		raise
	assert word and mean
	print '<ar><k>%s</k>' % (kssubscript.sub('\g<1>', word), )
	mean = mean.replace('\\n', '\n').replace('\\\n', '\\n')
	bold = False
	color = None
	indent = 0
	if mean[-1] == '\n':
		mean = mean[:-1]
	for str in mean.splitlines():
		if str.lstrip().startswith('[') and str.rstrip().endswith(']'):
			if seemsgmx(str):
				str = ampunquote(str.strip()[1:-1])
				print '<tr>%s</tr>' % (u''.join([gmx[ord(c)]
					for c in str]).encode('utf-8'),)
				continue
		ar = ampquote(str).split('//STE')
		result = [' ' * (indent/4), ar[0]]
		for s in ar[1:]:
			p = s.find('//')
			assert p > 0
			if s[:p].endswith('FONT'):
				if s.startswith('STD'):
					if bold and color:
						result.append('</c>')
						result.append('</b>')
						result.append('<c c="'+
								color +
								'">')
					elif bold:
						result.append('</b>')
					bold = False
				elif s.startswith('BOLD'):
					if not bold and color:
						result.append('</c>')
						result.append('<b>')
						result.append('<c c="'+
								color +
								'">')
					elif not bold:
						result.append('<b>')
					bold = True
				elif s.startswith('CURRENT'):
					if color:
						result.append('</c>')
						color = None
				else:
					if color:
						result.append('</c>')
					color = s[:s.index('FONT')]
					color = color.lower()
					assert color in ['black',
							'blue', 'red',
							'green',
							'yellow',
							'purple',
							'orange',
							'gray']
					if color == 'gray':
						color = 'brown'
					result.append('<c c="%s">' %
							(color,))
			elif s.startswith('HYPERLINK='):
				result.append('<iref>')
				result.append(s[10:p])
				result.append('</iref>')
			elif s.startswith('LEFTINDENT='):
				indent = int(s[11:p])
				if result[-1].endswith('\n'):
					pass
				elif len(result) > 1 and result[0]:
					result.append('\n')
				if indent > 0:
					result.append(' ' * (indent/4))
			elif s.endswith('ALIGN'):
				pass
			elif s == 'HORIZONTALLINE':
				if result[-1].endswith('\n'):
					pass
				else:
					result.append('\n')
				result.append('----\n')
			elif s == 'LINEBREAK':
				result.append('\n')
			else:
				raise Exception('Unrecognized ste tag '
						'STE' + s)
			result.append(s[p+2:])
		if result[-1] == '\n':
			del result[-1]
		result = removeemptycolortag.sub('', ''.join(result))
		result = kssubscript2.sub(r'<sub>\g<1></sub>', result)
		print result
	print '</ar>'
print '</xdxf>'

f.close()

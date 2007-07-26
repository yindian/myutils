#!/usr/bin/python
# -*- coding: utf-8 -*-
# BBS Text Formatter	by YIN Dian
# Hist:	070714: Completed the first seems-to-work version.
#	070715: Added debug mode switch and set words of alphanum unbreakable.
#		Several bug fixed.
#	070726: Fixed bug of line not breaking at the end of line or file.
#		Changed source file to unix format. Some other handy changes.
import sys, os, string, types, fileinput
from optparse import OptionParser
import UnicodeWidth
# constants
version = '20070726'
charwidth_ambinarrow = UnicodeWidth.wcwidth
charwidth_ambiwide = UnicodeWidth.wcwidth_cjk
endansi = '\033[0m'
linestartforbid = u',.!?)]}>»％、。，．：；！？·）｝〕〉》」』】〗’”'
lineendforbid = u'([{<«$（｛〔〈《「『【〖‘“'
intercharforbid = u'—…‥'
# debug function
debug = False
debug2 = False
debug3 = False
def DBG(*args):
	if debug:
		print >> sys.stderr,  ''.join(map(str, args)),
def DBG2(*args):
	if debug2:
		print >> sys.stderr,  ''.join(map(str, args)),
		#exec('print >> sys.stderr, ' + `args`[1:-1])
def DBG3(*args):
	if debug3:
		print >> sys.stderr,  ''.join(map(str, args)),
		#exec('print >> sys.stderr, ' + `args`[1:-1])

def getoptions():
	usage = '%prog [options] [filename(s)]\n\n\
BBS Text Formatter v.'+version+'\tcoded by YIN Dian.\n\
Functionalities:\n  1. Wrap the text considering punctuation prohibitions.\n\
  2. Reformat or filter out ANSI escape sequences.'
	parser = OptionParser(usage, version='%prog v.'+version)
	parser.set_defaults(filteransi=False, textwidth=76, maxwidth=78,
			tabsize=4, punctprohibit=True, joinline=False, 
			ambiwide=True, encoding='gbk', outfile='',
			expandtab=False)
	parser.add_option('-a', '--ansi', action='store_false',
			dest='filteransi', help='Reserve and reformat ANSI' +
			' escape sequences (default)')
	parser.add_option('-A', '--noansi', action='store_true',
			dest='filteransi', help='Filter out ANSI escape ' +
			'sequences')
	parser.add_option('-w', '--width', metavar='WIDTH', type='int',
			dest='textwidth', help='Set text wrapping width to ' +
			'WIDTH, default is %default')
	parser.add_option('-W', '--maxwidth', metavar='WIDTH', type='int',
			dest='maxwidth', help='Set max width of a line ' +
			'to WIDTH, default is %default')
	parser.add_option('-p', '--punct', action='store_true',
			dest='punctprohibit', help='Consider punctuation ' +
			'prohibitions (default)')
	parser.add_option('-P', '--nopunct', action='store_false',
			dest='punctprohibit', help='Don\'t consider ' +
			'punctuation prohibitions')
	parser.add_option('-j', '--join', action='store_true',
			dest='joinline', help='Treat consecutive non-blank ' +
			'lines as a paragraph')
	parser.add_option('-J', '--nojoin', action='store_false',
			dest='joinline', help='Treat each line as a ' +
			'paragraph to wrap (default)')
	parser.add_option('-m', '--ambi', action='store_true',
			dest='ambiwide', help='Treat CJK ambiguous characters'
			+ ' as wide (default)')
	parser.add_option('-M', '--noambi', action='store_false',
			dest='ambiwide', help='Treat CJK ambiguous characters'
			+ ' as narrow')
	parser.add_option('-t', '--expandtab', action='store_true',
			dest='expandtab', help='Expand tab to spaces')
	parser.add_option('-T', '--noexpandtab', action='store_false',
			dest='expandtab', help='Don\'t expand tab to spaces' +
			' (default)')
	parser.add_option('-s', '--tabsize', metavar='SIZE', type='int',
			dest='tabsize', help='Set tab size to SIZE, default' +
			' is %default')
	parser.add_option('-e', '--encoding', '--enc', dest='encoding',
			metavar='ENC', help='Set input/output encoding to ' +
			'ENC (default is %default)')
	parser.add_option('-o', '--output', dest='outfile', metavar='FILE',
			help='Output to file FILE (default to stdout)')
	parser.add_option('-D', '--debug', dest='debug', metavar='MODE',
			help='Set debug mode to MODE (default is %default)')
	return parser.parse_args()

def isblankline(line):
	for char in line:
		if not char.isspace():
			return False
	return True

def isalphanum(char):
	return (ord(char) < 0x2e80 and ord(char) > 32 and 
			not char.isspace() and not char in string.punctuation)

##### Punctuation Prohibition handling part #####
def breakword_with_jinze(word):
	"arg word = buftext\nreturn buftext, oktext"
	if len(word) < 2:
		if word.isspace():
			return u'', word
		else:
			return word, u''
	if word[-2] in lineendforbid: # x(x
		return word, u''
	if word[-2] in linestartforbid: # x)x
		if word[-1] in linestartforbid or word[-1] in intercharforbid:
			return word, u'' # x))
		else:
			return word[-1], word[:-1] # x)x
	if word[-1] in linestartforbid: # xx)
		return word, u''
	if word[-2] in intercharforbid: # x-x
		if word[-1] in intercharforbid: # x--
			return word, u''
	if isalphanum(word[-1]) and isalphanum(word[-2]):
		return word, u''
	return word[-1], word[:-1]

def breakword_without_jinze(word):
	if word:
		return word[-1], word[:-1]
	else:
		return word, u''

##### the main stuff #####
def bbsformat(text, options, ansistatus='', currentpos=0, outfile=sys.stdout,
		buftext = u'', bufwidth = 0):
	text = unicode(text, options.encoding, 'replace')
	text = text.split(u'\n')
	if text[-1] == '':
		del(text[-1])
	DBG(text[0][:40].encode(options.encoding, 'replace') + '  |  ' + `len(text)`)
	tabsize = options.tabsize
	maxwidth = options.maxwidth
	textwidth = options.textwidth
	joinline = options.joinline
	filteransi = options.filteransi
	expandtab = options.expandtab
	enc = options.encoding
	if options.ambiwide:
		charwidth = charwidth_ambiwide
	else:
		charwidth = charwidth_ambinarrow
	if options.punctprohibit:
		breakword = breakword_with_jinze
	else:
		breakword = breakword_without_jinze
	oktext = u''
	okwidth = 0
	escapemode = False
	for line in text:
		if joinline and isblankline(line):
			DBG2('('+buftext.encode(enc, 'replace')+')',)
			DBG2('<'+ansistatus+'>',)
			if ansistatus and \
				currentpos == 0: # BOL
				DBG('(m)')
				outfile.write(ansistatus)
			currentpos += bufwidth
			if currentpos > maxwidth:
				while buftext and buftext[0].isspace():
					bufwidth -= charwidth(buftext[0])
					buftext = buftext[1:]
				if ansistatus:
					outfile.write(endansi +
					'\n' + ansistatus)
					outfile.write(
					buftext.encode(enc, 
					'replace'))
				else:
					outfile.write('\n' +
					buftext.encode(enc,
					'replace'))
				currentpos = bufwidth
			else:
				if currentpos >= textwidth:
					outfile.write(buftext.encode(enc,
						'replace').rstrip())
					if ansistatus:
						outfile.write(
						endansi + '\n'
						+ ansistatus)
					else:
						outfile.write('\n')
					currentpos = 0
				else:
					outfile.write(buftext.encode(enc,
						'replace'))
			if currentpos: # not BOL
				if ansistatus:
					outfile.write(endansi)
				outfile.write('\n')
			outfile.write('\n')
			buftext = u''
			currentpos = bufwidth = 0
		else:
			for char in line: # char can never be '\n', hehe
				# oktext = u'' at the beginning
				if escapemode:
					ansistatus += char
					if char == u'm':
						escapemode = False
						if not filteransi:
							outfile.write(ansistatus)
							if ansistatus == endansi:
								ansistatus = ''
						else:
							ansistatus = ''
					continue
				elif char == u'\t':
					okwidth = int((currentpos + bufwidth) 
					/ tabsize + 1) * tabsize - currentpos
					if expandtab:
						oktext = buftext + ' ' * (
							okwidth - bufwidth)
					else:
						oktext = buftext + char
					buftext = u''
					bufwidth = 0
				elif char == u'\033': # ANSI escape char
					# flush first
					DBG2('('+buftext.encode(enc, 'replace')+')')
					currentpos += bufwidth
					if currentpos > maxwidth:
						while buftext and buftext[0].isspace():
							bufwidth -= charwidth(buftext[0])
							buftext = buftext[1:]
						if ansistatus:
							outfile.write(endansi +
							'\n' + ansistatus)
							outfile.write(
							buftext.encode(enc, 
							'replace'))
						else:
							outfile.write('\n' +
							buftext.encode(enc,
							'replace'))
						currentpos = bufwidth
					else:
						if currentpos >= textwidth:
							outfile.write(buftext.encode(enc,
								'replace').rstrip())
							if ansistatus:
								outfile.write(
								endansi + '\n'
								+ ansistatus)
							else:
								outfile.write('\n')
							currentpos = 0
						else:
							outfile.write(buftext.encode(enc,
								'replace'))
					buftext = u''
					bufwidth = 0
					escapemode = True
					ansistatus = char
					continue
				else:
					buftext += char
					buftext, oktext = breakword(buftext)
					if oktext:
						okwidth = bufwidth
						bufwidth = 0
					bufwidth += charwidth(char)
				if oktext:
					DBG2('('+oktext.encode(enc, 'replace')+','+
							buftext.encode(enc, 'replace')+')')
					if currentpos + okwidth > maxwidth:
						while oktext and oktext[0].isspace():
							okwidth -= charwidth(oktext[0])
							oktext = oktext[1:]
						if ansistatus:
							outfile.write(endansi +
							'\n' + ansistatus)
							outfile.write(
							oktext.encode(enc, 
							'replace'))
						else:
							outfile.write('\n' +
							oktext.encode(enc,
							'replace'))
						currentpos = okwidth
					else:
						currentpos += okwidth
						if currentpos >= textwidth:
							outfile.write(oktext.encode(enc,
								'replace').rstrip())
							if ansistatus:
								outfile.write(
								endansi + '\n'
								+ ansistatus)
							else:
								outfile.write('\n')
							currentpos = 0
						#elif currentpos == okwidth:
						#	while oktext and oktext[0].isspace():
						#		okwidth -= \
						#		charwidth(oktext[0])
						#		oktext = oktext[1:]
						#	outfile.write(oktext.encode(enc,
						#		'replace'))
						else:
							outfile.write(oktext.encode(enc,
								'replace'))
					oktext = u''
					okwidth = 0
					DBG3('{'+`currentpos`+'}')
			if not joinline:
				DBG2('('+buftext.encode(enc, 'replace')+')',)
				DBG2('<'+ansistatus+'>',)
				if currentpos + bufwidth > maxwidth:
					buftext = buftext.strip()
					if ansistatus:
						outfile.write(endansi +
						'\n' + ansistatus)
						outfile.write(
						buftext.encode(enc, 
						'replace') + endansi)
					else:
						outfile.write('\n' +
						buftext.encode(enc,
						'replace'))
				else:
					outfile.write(buftext.encode(enc,
						'replace').rstrip())
					if ansistatus:
						outfile.write(endansi)
				outfile.write('\n')
				buftext = u''
				currentpos = bufwidth = 0
	return ansistatus, currentpos, buftext, bufwidth

if __name__ == '__main__':
	(options, args) = getoptions()
	if options.debug:
		debug  = options.debug.find('1') >= 0
		debug2 = options.debug.find('2') >= 0
		debug3 = options.debug.find('3') >= 0
	DBG(`options`+'\n')
	if options.outfile == '':
		outp = sys.stdout
	else:
		outp = open(options.outfile, 'w')
	ansistatus = buftext = u''
	currentpos = bufwidth = 0
	maxwidth = options.maxwidth
	enc = options.encoding
	for line in fileinput.input(args):
		if fileinput.isfirstline():
			if buftext:
				if currentpos + bufwidth > maxwidth:
					buftext = buftext.strip()
					if ansistatus:
						outp.write(endansi +
						'\n' + ansistatus)
						outp.write(
						buftext.encode(enc, 
						'replace') + endansi)
					else:
						outp.write('\n' +
						buftext.encode(enc,
						'replace'))
				else:
					outp.write(buftext.encode(enc,
						'replace').rstrip())
					if ansistatus:
						outp.write(endansi)
				outp.write('\n')
			ansistatus = ''
			currentpos = 0
			buftext = u''
			bufwidth = 0
		ansistatus, currentpos, buftext, bufwidth = bbsformat(line, 
				options, outfile=outp, ansistatus=ansistatus,
				currentpos=currentpos, buftext=buftext,
				bufwidth=bufwidth)
		DBG('\n' + 'ansistatus = ' + `ansistatus` + '   currentpos = '
				+ `currentpos` + '    buftext = \'' +
				buftext.encode(options.encoding) + 
				'\'   bufwidth = ' + `bufwidth` +'\n')
	if buftext:
		if currentpos + bufwidth > maxwidth:
			buftext = buftext.strip()
			if ansistatus:
				outp.write(endansi +
				'\n' + ansistatus)
				outp.write( buftext.encode(enc, 
				'replace') + endansi)
			else:
				outp.write('\n' +
				buftext.encode(enc,
				'replace'))
		else:
			outp.write(buftext.encode(enc,
				'replace').rstrip())
			if ansistatus:
				outp.write(endansi)
		outp.write('\n')

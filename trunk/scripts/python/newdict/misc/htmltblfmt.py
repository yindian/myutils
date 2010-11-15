#!/usr/bin/env python
import sys, os.path, string, re, types
from unicodedata import east_asian_width
from htmlentitydefs import name2codepoint
import pprint
#import pdb
try:
	import psyco
	psyco.full()
except:
	pass

fullwidthset = set(['F', 'W', 'A'])
isfullwidth = lambda c: east_asian_width(c) in fullwidthset
strwidth = lambda s: sum([isfullwidth(c) and 2 or 1 for c in s])

brtag = re.compile(r'<br\s*/?>', re.I)
paratag = re.compile(r'<p\s*/?>', re.I)
multispaces = re.compile(r'  +')
multilines = re.compile(r'\n\n\n+')
imgtag = re.compile(r'<img(?:[^>=]|="[^"]*"|=[^"])*>', re.I)
htmltag = re.compile(r'(<(?:[^>=]|="[^"]*"|=[^"])*>)')

def textcontent(s, enc='utf-8'):
	s = brtag.sub('\n', s.replace('\n', ' ')) # reformat new lines
	s = paratag.sub('\n\n', s) # reformat paragraphs
	s = multispaces.sub(' ', s)
	s = multilines.sub('\n\n', s)
	s = htmltag.sub('', s) # remove tags
	if type(s) != types.UnicodeType:
		s = s.decode(enc)
	ar = s.split('&')
	result = [ar[0]]
	for s in ar[1:]:
		p = s.find(';')         # not well-formed
		if p < 1:
			result.append('&')
		else:
			try:
				if s[0] == '#': # code point
					if p > 2 and s[1].lower() == 'x':
						code = int(s[2:p], 16)
					else:
						code = int(s[1:p], 0)
					result.append(unichr(code))
				else:           # html entity
					entity = s[:p].lower()
					result.append(unichr(name2codepoint[
						entity]))
				s = s[p+1:]
			except:
				result.append('&');
		result.append(s)
	return u''.join(result)

def textwidth(s, enc='utf-8'):
	return strwidth(textcontent(imgtag.sub('!!', s), enc))

def findprefix(ar, s, start=0, lower=string.lower):
	if lower is None:
		for i in xrange(start, len(ar)):
			if ar[i].startswith(s):
				return i
	else:
		for i in xrange(start, len(ar)):
			if lower(ar[i]).startswith(s):
				return i
	return -1

tagclosed = lambda s: s.endswith('>') and htmltag.match(s)
unpairedset = set(['br', 'hr', 'img'])
colspanpat = re.compile(r'colspan="?([0-9])+"?', re.I)
rowspanpat = re.compile(r'rowspan="?([0-9])+"?', re.I)
nbsptail = re.compile(r'(?:&nbsp;)+$')

def formattable(content, enc='utf-8'):
	ar = htmltag.split(content)
	numcol = 0
	maxnumcol = 0
	numrow = 0
	mat = []
	capt = None
	stack = []
	buf = []
	closing = False
	for s in ar:
		if s.startswith('<'):
			assert s.endswith('>')
			br = s.split()
			if len(br) == 1:
				br[0] = br[0][:-1]
			tag = br[0][1:].lower()
			closing = False
			if tag.startswith('/'):
				tag = tag[1:]
				try:
					assert stack[-1] == tag
				except:
					print >> sys.stderr, stack, s
					if stack[-2] == tag:
						del stack[-1]
						del stack[-1]
				else:
					del stack[-1]
				closing = True
			elif tag not in unpairedset and not s.endswith(
					'/>'):
				stack.append(tag)
			if not stack and closing:
				if tag == 'caption':
					buf = []
				elif tag == 'tr':
					buf = []
					numrow += 1
					maxnumcol = max(maxnumcol, numcol)
					numcol = 0
				else:
					raise Exception('Unknown tag '+tag)
			elif len(stack) == 1 and not closing:
				if tag == 'caption':
					capt = buf = []
				elif tag == 'tr':
					mat.append([])
				else:
					raise Exception('Unknown tag '+tag)
			elif len(stack)==2 and stack[0] == 'tr' and not closing:
				if tag in ('td', 'th'):
					colspan = rowspan = 1
					r = colspanpat.findall(s)
					if r:
						colspan = int(r[0])
					r = rowspanpat.findall(s)
					if r:
						rowspan = int(r[0])
					buf = []
					mat[numrow].append([colspan, rowspan,
							buf])
					numcol += colspan
				else:
					buf.append(s)
			elif len(stack) == 1 and stack[0] == 'tr' and closing:
				if tag not in ('td', 'th'):
					raise Exception('Unknown tag '+tag)
				mat[numrow][-1][2] = ''.join(mat[numrow][-1][2]
						).strip()
				buf = []
			else:
				buf.append(s)
		else:
			buf.append(s)
	retry = True
	while retry:
		retry = False
		colwidth = [0] * maxnumcol
		colspanwidthreq = []
		spanrows = [0] * maxnumcol
		for row in xrange(numrow):
			col = 0
			while col < maxnumcol and spanrows[col]:
				col += 1
			for i in xrange(len(mat[row])):
				colspan = mat[row][i][0]
				rowspan = mat[row][i][1]
				if col + colspan > maxnumcol:
					maxnumcol = col + colspan
					retry = True
					break
				for j in xrange(col, col+colspan):
					spanrows[j] = rowspan
				width = textwidth(mat[row][i][2])
				oldwidth = sum(colwidth[col:col+colspan])
				if oldwidth < width:
					if colspan == 1:
						colwidth[col] = width
					else:
						colspanwidthreq.append((col,
							colspan, width))
				col += colspan
				while col < maxnumcol and spanrows[col]:
					col += 1
			if retry:
				break
			for i in xrange(maxnumcol):
				if spanrows[i] > 0:
					spanrows[i] -= 1
		if retry:
			continue
		colspanwidthreq.sort()
		for col, colspan, width in colspanwidthreq:
			oldwidth = sum(colwidth[col:col+colspan])
			if oldwidth < width:
				colwidth[col+colspan-1] += width - oldwidth
	# now we have got colwidth
	spanrows = [0] * maxnumcol
	result = []
	for row in xrange(numrow):
		line = []
		col = 0
		while col < maxnumcol and spanrows[col]:
			line.append('&nbsp;' * colwidth[col])
			col += 1
		for i in xrange(len(mat[row])):
			colspan = mat[row][i][0]
			rowspan = mat[row][i][1]
			for j in xrange(col, col+colspan):
				spanrows[j] = rowspan
			width = textwidth(mat[row][i][2])
			newwidth = sum(colwidth[col:col+colspan])
			line.append(mat[row][i][2])
			line.append('&nbsp;' * (newwidth - width))
			col += colspan
			while col < maxnumcol and spanrows[col]:
				line.append('&nbsp;' * colwidth[col])
				col += 1
		for i in xrange(maxnumcol):
			if spanrows[i] > 0:
				spanrows[i] -= 1
		line = ''.join(line)
		line = nbsptail.sub('', line)
		line = line.replace('&nbsp;&nbsp;', '&#x3000;')
		result.append(line)
		result.append('<br>')
	#return pprint.pformat(mat) + '%dx%d' % (numrow, maxnumcol) + \
	#		pprint.pformat(colwidth)
	return ''.join(result)

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s filename.htm [enc]' % (os.path.basename(sys.argv[0]),)
	print 'Convert <table>...</table> to full-width-space-padded text'
	print 'Further post-processing is needed for a more useful result'
	print 'Supported tags inside: caption, tr, th, td. <table> is preserved'
	print 'Tag shall follow left bracket immediately'
	print 'Only cell text content, and col/row span are taken into account'
	print 'Newlines (<br>) in cell text are treated as spaces'
	print 'Padding space is &#x3000; + &nbsp;. Rows are delimited by <br>.'
	print 'Encoding is UTF-8 by default'
	sys.exit(0)

f = open(sys.argv[1], 'r')
enc = len(sys.argv) > 2 and sys.argv[2] or 'utf-8'

stack = []
content = []
openbracket = False
lineno = 0
for line in f:
	lineno += 1
	if not stack:
		if line.lower().find('<table') < 0:
			sys.stdout.write(line)
			continue
		ar = htmltag.split(line)
		p = ar[-1].find('<')
		if p > 0:
			ar.append(ar[-1][p:])
			ar[-2] = ar[-2][:p]
		i = findprefix(ar, '<table')
		if i < 0:
			sys.stdout.write(line)
			continue
		sys.stdout.write(''.join(ar[:i]))
		if i == len(ar) - 1 and not tagclosed(ar[i]):
			sys.stdout.write('<!-- %s --' % (ar[i][1:],))
		else:
			sys.stdout.write('<!-- %s -->' % (ar[i][1:-1],))
		i += 1
		stack = ['table']
		openbracket = False
		while i < len(ar):
			if ar[i].startswith('<'):
				if not tagclosed(ar[i]):
					assert i == len(ar) - 1
					openbracket = True
				br = ar[i].split()
				if len(br) == 1 and not openbracket:
					assert br[0].endswith('>')
					br[0] = br[0][:-1]
				tag = br[0][1:].lower()
				if tag.startswith('/'):
					tag = tag[1:]
					try:
						assert stack[-1] == tag
					except:
						print >> sys.stderr, 'L', lineno
						print >> sys.stderr, stack,ar[i]
						if stack[-2] == tag:
							del stack[-1]
							del stack[-1]
					else:
						del stack[-1]
				elif tag not in unpairedset and not ar[i
						].endswith('/>') and stack:
					stack.append(tag)
				if not stack and tag == 'table': # tbl complete
					try:
						sys.stdout.write(formattable(
							''.join(content), enc))
					except:
						print >> sys.stderr, 'L', lineno
						raise
					if openbracket:
						sys.stdout.write('<!-- %s --' %
								(ar[i][1:],))
					else:
						sys.stdout.write('<!-- %s -->' %
								(ar[i][1:-1],))
					content = []
				elif stack:
					content.append(ar[i])
				else:
					sys.stdout.write(ar[i])
			else:
				if stack:
					content.append(ar[i])
				else:
					sys.stdout.write(ar[i])
			i += 1
	else:
		ar = htmltag.split(line)
		p = ar[-1].find('<')
		if p > 0:
			ar.append(ar[-1][p:])
			ar[-2] = ar[-2][:p]
		openbracket = False
		for i in xrange(len(ar)):
			if ar[i].startswith('<'):
				if not tagclosed(ar[i]):
					assert i == len(ar) - 1
					openbracket = True
				br = ar[i].split()
				if len(br) == 1 and not openbracket:
					assert br[0].endswith('>')
					br[0] = br[0][:-1]
				tag = br[0][1:].lower()
				if tag.startswith('/'):
					tag = tag[1:]
					try:
						assert stack[-1] == tag
					except:
						print >> sys.stderr, 'L', lineno
						print >> sys.stderr, stack,ar[i]
						if stack[-2] == tag:
							del stack[-1]
							del stack[-1]
					else:
						del stack[-1]
				elif tag not in unpairedset and not ar[i
						].endswith('/>') and stack:
					stack.append(tag)
				if not stack and tag == 'table': # tbl complete
					try:
						sys.stdout.write(formattable(
							''.join(content), enc))
					except:
						print >> sys.stderr, 'L', lineno
						raise
					if openbracket:
						sys.stdout.write('<!-- %s --' %
								(ar[i][1:],))
					else:
						sys.stdout.write('<!-- %s -->' %
								(ar[i][1:-1],))
					content = []
				elif stack:
					content.append(ar[i])
				else:
					sys.stdout.write(ar[i])
			else:
				if stack:
					content.append(ar[i])
				else:
					sys.stdout.write(ar[i])
f.close()

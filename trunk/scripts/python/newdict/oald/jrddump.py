#!/usr/bin/env python
import sys, os.path, struct
import pdb, traceback

assert __name__ == '__main__'

if len(sys.argv) != 3:
	print 'Usage: %s conv.dat ovfl.dat' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'rb')
data = f.read()
f.close()
f = open(sys.argv[2], 'rb')
extra = f.read()
f.close()

NUL = '\0'
CTL = '\xff'
idx = 0
p = 0
pp = 0
while True:
	idx += 1
	binidx = struct.pack('!L', idx)
	p = data.find(binidx, p)
	while p >= 0 and ((p & 0x3) or data[p-1] != NUL):
		p = data.find(binidx, p+1)
	if p < 0:
		break
	p += 4
	while data[p] == NUL:
		p += 1
	q = p
	while data[q] not in (NUL, CTL, '=') and data[q:q+2] != ' /':
		q += 1
	word = data[p:q]
	p = q
	if data[p:p+2] == '\xff\0':
		p += 2
		try:
			pp = extra.index(binidx, pp)
		except:
			print >> sys.stderr, word, idx
			raise
		pp += 4
		q = pp
		while extra[q] != NUL:
			q += 1
		word += extra[pp:q]
		pp = q
	elif word.count('(') != word.count(')'):
		q = word.rindex('(') - 1
		while word[q] == ' ':
			q -= 1
		q += 1
		p -= len(word) - q
		word = word[:q]
		assert data[p:p+5].lstrip().startswith('(')
	#print word
	while True:
		while data[p] == NUL:
			p += 1
		while not (0x20 <= ord(data[p]) < 0x7F or data[p] == CTL):
			p += 1
		q = p
		while data[q] != NUL:
			q += 1
		if q >= p + 6:
			break
		else:
			p = q
	if data[q-1] == CTL:
		q += 1
	mean = data[p:q]
	p = q
	if mean[-2:] == '\xff\0':
		try:
			pp = extra.index(binidx, pp)
		except:
			print >> sys.stderr, word, idx
			raise
		pp += 4
		q = pp
		while extra[q] != NUL:
			q += 1
		mean = mean[:-2] + extra[pp:q]
		pp = q
	q = mean.find(' / ')
	if q > 0:
		if mean[:q].count(CTL) < 2:
			mean = mean[q+1:]
		else:
			mean = mean.lstrip()
			try:
				assert mean[0] in ('(', CTL)
			except:
				#print >> sys.stderr, word, idx, mean[:q]
				q = 0
				while mean[q] not in ('(', CTL):
					q += 1
				mean = mean[q:]
	else:
		mean = mean.lstrip()
		if (mean[0] not in '(/\xff' and not mean.startswith('=>')
				and not mean.startswith('= \xff') and not
				mean.startswith('=\xff')
				) or len(mean) < 4:
			q = mean.find('=')
			if 0 < q < 6:
				assert mean[q:q+6].find('\xff\x0f') > 0
				mean = mean[q:]
			elif 0 < mean.find(CTL) < 4:
				mean = mean[mean.index(CTL):]
			elif 0 < mean.find(' (') < 4:
				mean = mean[mean.index('('):]
			elif 0 < mean.find('/ ') < 4:
				mean = mean[mean.index('/'):]
			else:
				print >> sys.stderr, word, idx, mean[:32]
	ar = mean.split(CTL)
	result = [ar[0]]
	for s in ar[1:]:
		c = s[0]
		if c == 'I':
			result.append('<i>')
		elif c == 'i':
			result.append('</i>')
		elif c == 'B':
			result.append('<b>')
		elif c == 'b':
			result.append('</b>')
		elif c == 'X':
			result.append('<font face="phoneticplain">')
		elif c == 'x':
			result.append('</font>')
		elif c == 'P':
			result.append('<sup>')
		elif c == 'p':
			result.append('</sup>')
		elif c == 'W':
			result.append('<span class="chn">')
		elif c == 'w':
			result.append('</span>')
		elif c == '\x0f':
			result.append('<a href="bword://')
		elif c == '\x10':
			result.append('">')
		elif c == '\x11':
			result.append('</a>')
		else:
			raise Exception('Unknown control code %s' % (`c`,))
		result.append(s[1:])
	mean = ''.join(result)
	#try:
	#	mean = mean.decode('cp950').encode('utf-8')
	#except:
	#	print >> sys.stderr, word, idx
	#	traceback.print_exc()
	#	pdb.set_trace()
	print '%s\t%s' % (word, mean.replace('\n', '<br>'))
idx -= 1
print >> sys.stderr, 'Total word:', idx

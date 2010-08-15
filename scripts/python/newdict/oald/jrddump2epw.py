#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, re
import pdb, traceback

def reformat(mean):
	#return mean
	lines = mean.split('<br>')
	result = ['<p>']
	lastitem = 0
	num = None
	for line in lines:
		ar = line.split('<b>')
		result.append(ar[0])
		lasts = ar[0]
		lastnum = False
		for s in ar[1:]:
			p = s.index('</b>')
			newline = False
			if p<4 or s[0]in'~&#`,' or s[:p].rstrip()[-1].isdigit():
				if p < 4:
					t = s[:p].strip()
				else:
					t = s[:p].rstrip().split()[-1]
				try:
					if t.isdigit() and t != '45':
						num = int(t)
						if word == 'perk' and num == 3:
							lastitem = 2
						assert num<=1 or num==lastitem+1
						if num > 0:
							lastitem = num
							newline = True
							lastnum = True
					elif len(t) == 1:
						if t.isalpha():
							if s[0] == '~':
								pass
							elif 'a' <= t < 'm'and((
								s[p+4] == ')'
								)):
								if not lastnum:
									newline = True
							#elif t.isupper():
							#	assert t in ((
							#		'ACDEF'
							#		'GIJKL'
							#		'MNSOR'
							#		'WY'
							#		))
							#else:
							#	assert t in ((
							#		'msprv'
							#		'xy'
							#		))
						else:
							assert t in '=~().%+'
						lastnum = False
				except:
					print >> sys.stderr, lastitem,(
							num), t, lasts,'|',s
					raise
			else:
				lastnum = False
			if newline:
				if s[p+4:p+5] == ')' and lasts.endswith('('):
					try:
						assert result[-1].endswith('(')
					except:
						print >> sys.stderr, s
						print >> sys.stderr, lasts
						print >> sys.stderr, result[-1]
						print >> sys.stderr, result
						raise
					result[-1] = result[-1][:-1]
					result.append('</p>\n<p>(<b>')
					result.append(s)
				else:
					p -= 1
					while p > 0 and s[p].isspace():
						p -= 1
					while p > 0 and not s[p].isspace():
						p -= 1
					if p == 0 or not s[:p].strip():
						result.append('</p>\n<p><b>')
						result.append(s)
					else:
						result.append('<b>')
						result.append(s[:p])
						result.append('</b></p>\n<p><b>')
						result.append(s[p:])
			else:
				p = s.index('</b>')
				result.append('<dfn>')
				result.append(s[:p])
				result.append('</dfn>')
				result.append(s[p+4:])
			lasts = s
		result.append('</p>\n<p>')
	result.append('</p>')
	mean = ''.join(result)
	return mean

assert __name__ == '__main__'

if len(sys.argv) != 3:
	print 'Usage: %s utf8_dump ill_dir' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'rb')

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
<title>牛津高階英漢詞典第四版</title>
</head>
<body>"""

phpua = lambda s: ''.join([(0x30 <= ord(c) < 0x60 or 0x7B <= ord(c) < 0x7F)
	and '&#x%04X;' % (ord(c) + 0xE000,) or c for c in s])
quote = lambda s: s.replace('>', '&gt;')
wordlist = []
reflist = []
refmap = {
		'swimming': 'swim',
		'etc': 'et cetera',
		'uncalled': 'uncalled-for',
		'draughts': 'draught',
		'eau': 'eau-de-Cologne',
		'doing': 'do2',
		'boxing': 'box2',
		'anti-clockwise': 'anticlockwise',
		'haute': 'haute couture',
		'cul': 'cul-de-sac',
		'facto': 'de facto',
		'Domesday': 'Domesday Book',
		'Julian': 'Julian calendar',
		'haem': 'haem(o)-',
		'Rt': 'Rt Hon.',
		'Lords': 'lord',
		'Heaviside': 'Heaviside layer',
		'Gordian': 'Gordian knot',
		'Litt': 'DLitt.',
		'madame': 'Madame.',
		'East': 'east.',
		'knick': 'knick-knack',
		'tenpin': 'tenpin bowling',
		'Fallopian': 'Fallopian tube',
		'palae': 'palae(o)-',
		'Parthian': 'Parthian shot',
		'paed': 'paed(o)-',
		'carbolic': 'carbolic acid',
		'bubonic': 'bubonic plague',
		'self-raising': 'self-raising flour',
		'wester': 'sou\'wester',
		'-': 'upset',
		'deser': 'deserve',
		}
for line in f:
	word, mean = line.rstrip().split('\t', 1)
	syn = word.split(', ')
	sup = 0
	if mean.startswith('<sup>'):
		p = mean.index('</sup>', 5)
		sup = int(mean[5:p])
		mean = mean[p+6:].lstrip()
	if sup == 0:
		if syn[-1] == syn[0].lower() or syn[0].replace('(','').replace(
				')', '') == syn[-1]:
			uniqword = syn[-1]
		else:
			uniqword = syn[0]
		if mean.find('<i>abbr ', 0, 100) >= 0:
			uniqword += '.'
		elif mean.find('<i>pref ') >= 0 and uniqword in wordlist:
			uniqword += '-'
	else:
		uniqword = syn[0] + `sup`
	try:
		assert uniqword not in wordlist
	except:
		print >> sys.stderr, word, sup
		raise
	wordlist.append(uniqword)
f.close()
f = open(sys.argv[1], 'rb')
for line in f:
	word, mean = line.rstrip().split('\t', 1)
	syn = word.split(', ')
	sup = 0
	if mean.startswith('<sup>'):
		p = mean.index('</sup>', 5)
		sup = int(mean[5:p])
		mean = mean[p+6:].lstrip()
	if sup == 0:
		if syn[-1] == syn[0].lower() or syn[0].replace('(','').replace(
				')', '') == syn[-1]:
			uniqword = syn[-1]
		else:
			uniqword = syn[0]
		if mean.find('<i>abbr ', 0, 100) >= 0:
			uniqword += '.'
		elif mean.find('<i>pref ') >= 0 and uniqword in wordlist:
			uniqword += '-'
	else:
		uniqword = syn[0] + `sup`
	print '<dl>\n<dt id="%s">%s</dt>' % (uniqword, sup and '%s<sup>%s</sup>'
			% (word, `sup`) or word)
	if len(syn) > 1:
		for s in syn:
			print '<key type="表記">%s</key>' % (s,)
	print '<dd>'
	ar = mean.split('<')
	result = [quote(ar[0])]
	stack = []
	i = 1
	phonetic = False
	lastref = None
	lastrefpos = -1
	for s in ar[1:]:
		try:
			p = s.index('>')
			if s.startswith('/'):
				assert stack[-1].startswith(s[1:p])
				del stack[-1]
				if s.startswith('/font'):
					phonetic = False
				elif s[1:p] == 'a':
					assert lastref is not None
					if i+1 < len(ar) and ar[i+1].startswith(
							'sup') and p+2>len(s):
						pass
					else:
						if lastref not in wordlist:
							if lastref.lower() in wordlist:
								lastref = lastref.lower()
							elif lastref+'1' in wordlist:
								lastref += '1'
							elif lastref.lower()+'1' in wordlist:
								lastref = lastref.lower()+'1'
							elif lastref+'.' in wordlist:
								lastref += '.'
							elif lastref+'-' in wordlist:
								lastref += '-'
							elif '-'+lastref in wordlist:
								lastref = '-'+lastref
							if lastref.title() in wordlist:
								lastref = lastref.title()
							elif refmap.has_key(lastref):
								lastref = refmap[lastref]
						assert lastref in wordlist
						reflist.append((lastref, word))
						result.insert(lastrefpos,
								'<a href="#%s">'
								% (lastref,))
						result.append('</a>')
						lastref = None
						lastrefpos = -1
				elif s[1:p] in ('i', 'b', 'sup'):
					result.append('<%s>' % (s[:p],))
					if s[1:p] == 'sup' and lastref:
						try:
							ss = int(result[-2])
						except:
							print >> sys.stderr, word, lastref, result[-2]
							q= result[-2].index(',')
							ss = int(result[-2][:q])
						if lastref+`ss` in wordlist:
							lastref += `ss`
						elif lastref.replace('-','')+`ss` in wordlist:
							lastref = lastref.replace('-','')+`ss`
						else:
							assert lastref in wordlist
						reflist.append((lastref,
							word))
						result.insert(lastrefpos,
								'<a href="#%s">'
								% (lastref,))
						result.append('</a>')
						lastref = None
						lastrefpos = -1
			else:
				stack.append(s[:p])
				if s.startswith('font'):
					#assert ar[i+1].startswith('/font>')
					phonetic = True
				elif s[:p] in ('i', 'b', 'sup'):
					result.append('<%s>' % (s[:p],))
				elif s[:p] == 'br':
					del stack[-1]
					result.append('<br>')
				elif s.startswith('SYMFONT'):
					assert p == 8
					del stack[-1]
					result.append('&#x%04X;' % (ord(s[7])
						+ 0xE000, ))
				elif s.startswith('a '):
					q = s.index('bword://') + 8
					lastref = s[q:p-1]
					if lastref[-1] == ' ' and s[-1] != ' ':
						s += ' '
					lastref = lastref.rstrip()
					lastrefpos = len(result)
			s = s[p+1:]
			if phonetic:
				br = s.split('&')
				res = [phpua(br[0])]
				for t in br[1:]:
					p = t.find(';')
					if p > 0:
						res.append(t[:p+1])
						res.append(phpua(t[p+1:]))
					else:
						res.append('&amp;')
						res.append(phpua(t))
				s = ''.join(res)
			result.append(quote(s).decode('utf-8').encode('sjis',
					'xmlcharrefreplace'))
		except:
			print >> sys.stderr, word, sup, i, s, stack, lastref
			raise
		i += 1
	mean = ''.join(result)
	try:
		mean = reformat(mean)
	except:
		print >> sys.stderr, word, sup
		raise
	print mean
	print '</dd>'
	print '</dl>'

f.close()
print """\
</body>
</html>"""

for ref, word in reflist:
	try:
		assert ref in wordlist
	except:
		print >> sys.stderr, ref, word

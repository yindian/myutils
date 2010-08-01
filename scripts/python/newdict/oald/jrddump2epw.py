#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, re
import pdb, traceback

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
for line in f:
	word, mean = line.rstrip().split('\t', 1)
	syn = word.split(', ')
	sup = 0
	if mean.startswith('<sup>'):
		p = mean.index('</sup>', 5)
		sup = int(mean[5:p])
		mean = mean[p+6:].lstrip()
	if sup == 0:
		if syn[-1] == syn[0].lower():
			uniqword = syn[-1]
		else:
			uniqword = syn[0]
		if mean.find('<i>abbr ') >= 0:
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
	print '<dl>\n<dt id="%s">%s</dt>' % (uniqword, sup and '%s<sup>%s</sup>'
			% (word, `sup`) or word)
	if len(syn) > 1:
		for s in syn[1:]:
			if s.lower() != syn[0].lower():
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
							'sup'):
						pass
					else:
						#assert lastref in wordlist
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
						#assert lastref+`ss` in wordlist
						reflist.append((lastref+`ss`,
							word))
						result.insert(lastrefpos,
								'<a href="#%s">'
								% (lastref+
									`ss`,))
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
						res.append(phpua(t))
				s = ''.join(res)
			result.append(quote(s).decode('utf-8').encode('sjis',
					'xmlcharrefreplace'))
		except:
			print >> sys.stderr, word, sup, i, s, stack, lastref
			raise
		i += 1
	mean = ''.join(result)
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
		print ref, word

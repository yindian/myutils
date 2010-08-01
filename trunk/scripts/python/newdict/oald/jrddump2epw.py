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

wordlist = []
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
	print '<dd>'
	print '</dd>'
	print '</dl>'

f.close()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import psyco
	psyco.full()
except:
	pass

def fwalpha2hw(str):
	result = []
	for c in str:
		if 0xFF01 <= ord(c) <= 0xFF5E:
			result.append(unichr(ord(c) - 0xFF00 + 0x20))
		else:
			result.append(c)
	return u''.join(result)

import sys
for line in sys.stdin:
	line = unicode(line[:-1], 'utf-8')
	word, mean = line.split(u'\t')
	means = mean.split(u'\\n')
	for i in range(len(means)):
		mean = means[i]
		if mean.startswith(u'注音一式:') or mean.startswith(u'注音二式:') or mean.startswith(u'通用拼音:') or mean.startswith(u'詞目:') or mean.startswith(u'相似詞:') or mean.startswith(u'相反詞:'):
			mean = mean + u'\\n'
		elif mean.startswith(u'注釋:'):
			pass
		elif (mean.startswith(u'（') and mean.endswith(u'）')) or mean.startswith(u'資料來源:'):
			mean = u'\\n' + mean
		else:
			mean0 = mean
			mean = mean.lstrip()
			if mean and (0x3220 <= ord(mean[0]) < 0x3226 or 0x2474 <= ord(mean[0]) < 0x2483 or 0xE286 <= ord(mean[0]) < 0xE29C or 0xE2E5 <= ord(mean[0]) < 0xE2ED or ord(mean[0]) in [0xE2F2, 0xE834, 0xE909, 0xE90A, 0xE917, 0xEB1B] or (len(mean) >= 3 and mean[0] == '(' and mean[2] == ')')):
				mean = u'\\n' + mean0
		means[i] = mean
	mean = u''.join(means)
	print (word + u'\t' + mean).encode('utf-8')

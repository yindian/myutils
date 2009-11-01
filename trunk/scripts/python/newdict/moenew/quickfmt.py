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

def subsgaiji(str):
	quickmap = (
			(u'<?9CDA>', u'å'),
			(u'<?9CDB>', u'e̊'),
			(u'<?9CDC>', u'i̊'),
			(u'<?9CDD>', u'o̊'),
			(u'<?9CDE>', u'ů'),
			(u'<?FE50>', u'〖'),
			(u'<?FE51>', u'〗'),
			(u'<?FE52>', u'㈠'),
			(u'<?FE53>', u'㈡'),
			(u'<?FE54>', u'㈢'),
			(u'<?FE55>', u'㈣'),
			(u'<?FE56>', u'㈤'),
			(u'<?FE57>', u'㈥'),
			(u'<?FE59>', u'⑴'),
			(u'<?FE5A>', u'⑵'),
			(u'<?FE5B>', u'⑶'),
			(u'<?FE5C>', u'⑷'),
			(u'<?FE5D>', u'⑸'),
			(u'<?FE5E>', u'⑹'),
			(u'<?FE5F>', u'⑺'),
			(u'<?FE60>', u'⑻'),
			(u'<?FE61>', u'⑼'),
			(u'<?FE62>', u'⑽'),
			(u'<?FE63>', u'⑾'),
			(u'<?FE64>', u'⑿'),
			(u'<?FE65>', u'⒀'),
			(u'<?FE66>', u'⒁'),
			(u'<?FE67>', u'⒂'),
			(u'<?FE68>', u'ā'),
			(u'<?FE69>', u'á'),
			(u'<?FE6A>', u'ǎ'),
			(u'<?FE6B>', u'à'),
			(u'<?FE6C>', u'ē'),
			(u'<?FE6D>', u'é'),
			(u'<?FE6E>', u'ě'),
			(u'<?FE6F>', u'è'),
			(u'<?FE70>', u'ī'),
			(u'<?FE71>', u'í'),
			(u'<?FE72>', u'ǐ'),
			(u'<?FE73>', u'ì'),
			(u'<?FE74>', u'ō'),
			(u'<?FE75>', u'ó'),
			(u'<?FE76>', u'ǒ'),
			(u'<?FE77>', u'ò'),
			(u'<?FE78>', u'r̄'),
			(u'<?FE79>', u'ŕ'),
			(u'<?FE7A>', u'ř'),
			(u'<?FE7B>', u'r̀'),
			(u'<?FE7C>', u'ū'),
			(u'<?FE7D>', u'ú'),
			(u'<?FE7E>', u'ǔ'),
			(u'<?FEA1>', u'ù'),
			(u'<?FEA2>', u'z̄'),
			(u'<?FEA3>', u'ź'),
			(u'<?FEA4>', u'ž'),
			(u'<?FEA5>', u'z̀'),
			(u'<?FED3>', u'(名)'),
			(u'<?FED4>', u'(動)'),
			(u'<?FED5>', u'(形)'),
			(u'<?FED6>', u'(副)'),
			(u'<?FED7>', u'(助)'),
			(u'<?FED8>', u'(介)'),
			(u'<?FED9>', u'(歎)'),
			(u'<?FEDA>', u'(連)'),
			)
	for from_, to_ in quickmap:
		str = str.replace(from_, to_)
	return str

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
		elif mean.lstrip().startswith(u'<?FE') or (mean.startswith(u'（') and mean.endswith(u'）')) or mean.startswith(u'資料來源:'):
			mean = u'\\n' + mean
		else:
			#try:
			#	assert i == 0 or means[i-1].startswith(u'注釋:') or not mean or mean[0].isspace()
			#except:
			#	print >> sys.stderr, word.encode('gbk', 'replace'), mean.encode('gbk', 'replace')
			#	pass
			mean = mean.lstrip()
		mean = subsgaiji(mean)
		if mean.startswith(u'注音一式:') or mean.startswith(u'注音二式:') or mean.startswith(u'通用拼音:'):
			mean = fwalpha2hw(mean)
		means[i] = mean
	mean = u''.join(means)
	print (word + u'\t' + mean).encode('utf-8')

#!/usr/bin/env python
import sys
import glob
import re
import libxml2dom
import pdb

#colpat = re.compile(r'<!--Collins[^>]*-->(.*?)<!--Collins End-->', re.S)
colpat = re.compile(r'<!--Collins Start-->(.*?)<!--Collins End-->', re.S)
spcpat = re.compile(r'''[ 	\r]+''')
wordgrampat = re.compile(r'<div ([^>]*) id="word_gram[^>]*">')
wordhrefpat = re.compile(r'href="/([^"]*)"')
def ref2h(m):
	return 'href="bword://%s"' % (m.group(1).replace('_', ' '),)

def getmeaning(doc):
	result = []
	pdb.set_trace()
	items = doc.firstChild.firstChild
	#assert items.tag == 'collins_en_cn')
	for item in items:
		result.append(items.textContent)
	return '\\n'.join(result)

assert __name__ == '__main__'

try:
	f = open('style.css')
except:
	f = open('../style.css')
style = '<style type="text/css">\n' + f.read() + '</style>\n'
f.close()
style = style.replace('\r\n', '\\n').replace('\n', '\\n')
flist = glob.glob('*')
flist.sort()
result = []
for fname in flist:
	f = open(fname)
	buf = f.read()
	f.close()
	try:
		buf = colpat.findall(buf)[0]
	except:
		print >> sys.stderr, 'Not found in', fname
		continue
	result.append(fname)
	result.append('\t')
	result.append(style)
	buf = wordgrampat.sub('<div>', buf)
	buf = wordhrefpat.sub(ref2h, buf)
	result.append(spcpat.sub(' ', buf).replace('\n', '\\n'))
	#doc = libxml2dom.parseString(spcpat.sub(' ', buf), html=1)
	#result.append(getmeaning(doc))
	result.append('\n')
print ''.join(result)

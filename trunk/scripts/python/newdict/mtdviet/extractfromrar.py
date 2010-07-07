#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re
import UnRAR2

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s file.rar' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

rf = UnRAR2.RarFile(sys.argv[1])
outf = open('out.txt', 'w')
logf = open('log.txt', 'w')
wordpat = re.compile(r"<span id='tdwrd'.*?>(.*?)</span>")

count = 0
for info, buf in rf.fileiter():
	name = info.wfilename.encode('gb18030')
	try:
		ar = name.split('%')
		res = [ar[0]]
		for s in ar[1:]:
			assert s[0] in '89'
			res.append(chr(int(s[:2], 16)))
			res.append(s[2:])
		name = ''.join(res).replace('?', '@')
		name = name.decode('utf-8')
		#print `name`
	except:
		#print >> sys.stderr, 'Cannot decode', `name`
		pass
	count += 1
	if count % 500 == 0:
		print '=============== count = %d ==================='% (count,)
	p = buf.find('tdContent')
	if p < 0:
		print >> sys.stderr, 'tdContent not found in', `name`
		print >> logf, 'tdContent not found in', `name`
		continue
	p, q = buf.rfind('\n', 0, p), buf.find('\n', p)
	cont = buf[p+1:q].strip()
	if cont.find('class="not_found"') > 0:
		#print >> sys.stderr, 'ket qua not found in', `name`
		print >> logf, 'ket qua not found in', `name`
		continue
	try:
		word = wordpat.findall(cont)[0]
	except:
		print >> logf, 'tdwrd not found in', `name`
		continue
	print >> outf, '%s\t%s' % (word, cont)
	#try:
	#	f = open(name, 'wb')
	#except IOError:
	#	os.makedirs(os.path.split(name)[0])
	#	f = open(name, 'wb')
	#f.write(buf)
	#f.close()
outf.close()
logf.close()

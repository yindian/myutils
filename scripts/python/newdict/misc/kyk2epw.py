#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, sqlite3, re
import pdb

assert __name__ == '__main__'
if len(sys.argv) != 2:
	print 'Usage: %s db_file' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
</head>
<body>
<dl>"""

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()
field='bGluZSxjYXRlZ29yeSxjYXRlZ29yeV9zdWI='
table='a2FueW9rdV9zdWI='
c.execute('select %s from %s' % (field.decode('base64'),table.decode('base64')))
catmap = {}
catsubmap = {}
catsubitems = {}
catlist = []
for code, cat, catsub in c:
	catmap[code] = catsub
	catmap[catsub] = code
	if catsubmap.has_key(catsub):
		assert catsubmap[catsub] == cat
	else:
		catsubmap[catsub] = cat
		if not catlist or catlist[-1][0] != cat:
			catlist.append([cat, []])
		catsubitems[catsub] = []
		catlist[-1][1].append([catsub, catsubitems[catsub]])
field='dGl0bGUseW9taSxjb21tZW50LHN5bm9ueW0sYW50b255bSxyZWZmZXJlbmNlLGJhZCxsaW5l'
c.execute('select %s from item' % (field.decode('base64'),))

enc = lambda s: s.encode('cp932')

idx = 0
for title, pron, mean, syn, ant, ref, bad, cat in c:
	idx += 1
	if pron == title:
		print '<dt id="%d">%s</dt>' % (idx, enc(pron))
	else:
		print '<dt id="%d">%s【%s】</dt>' % (idx, enc(title), enc(pron))
	print '<p>%s</p>' % (enc(mean).replace('\n', '<br>'),)
	print '<p>'
	if syn:
		print '【同義】%s' % (enc(syn),)
	if ant:
		print '【反義】%s' % (enc(ant),)
	if ref:
		print '【参照】%s' % (enc(ref),)
	if bad:
		print '【誤用】%s' % (enc(bad),)
	print '<a href="toc.htm#%s">↑</a>' % (`cat`+enc(title),)
	catsubitems[catmap[cat]].append((pron, title, idx))
	print '</p>'
c.close()

print >> sys.stderr, '<html>\n<body>'
print >> sys.stderr, '<p>'
for cat, subs in catlist:
	print >> sys.stderr, '<div id="%s"><a href="%s">%s</a><br></div>' % (
			'_'+enc(cat), enc(cat), enc(cat))
print >> sys.stderr, '</p>'
for cat, subs in catlist:
	print >> sys.stderr, '<h1 id="%s">%s</h1>' % (
			enc(cat), enc(cat))
	print >> sys.stderr, '<p>'
	for catsub, items in subs:
		print >> sys.stderr, '<div id="%s"><a href="%s">%s</a> <a href="%s">↑</a><br></div>' % (
				'_'+`catmap[catsub]`,
				catmap[catsub], enc(catsub),
				'_'+enc(cat))
	print >> sys.stderr, '</p>'
	for catsub, items in subs:
		items.sort()
		print >> sys.stderr, '<h2 id="%s">%s</h2>' % (catmap[catsub], enc(catsub))
		print >> sys.stderr, '<p>'
		for pron, title, idx in items:
			print >> sys.stderr, '<div id="%s">%s <a href="%s">↑</a><br></div>' % (
					`catmap[catsub]`+enc(title), enc(pron), '_'+`catmap[catsub]`)
			print >> sys.stderr, '<div><a href="out.htm#%d">%s</a><br></div>'%(
					idx, enc(title))
		print >> sys.stderr, '</p>'
print >> sys.stderr, '</body>\n</html>'

print """\
</dl>
</body>
</html>"""

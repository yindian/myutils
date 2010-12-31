#!/usr/bin/env python
import sys, os.path, string
import ConfigParser, StringIO
import pprint, pdb

def splitheadbody(mbsrc):
	if mbsrc.startswith(u'\ufeff'):
		mbsrc = mbsrc[1:]
	p = mbsrc.find('[Text]')
	if p >= 0:
		p = mbsrc.index('\n', p) + 1
		return mbsrc[:p], mbsrc[p:]
	return u'', mbsrc

assert __name__ == '__main__'
enc = lambda s: s.encode('gb18030')

if len(sys.argv) < 3:
	print 'Usage: %s from_mb.txt to_mb.txt'%(os.path.basename(sys.argv[0]),)
	print 'Convert ImegenU MB dump (UTF-16LE) to yong MB format (GB18030)'
	sys.exit(0)

f = open(sys.argv[1], 'rb')
mb = f.read().decode('utf-16le')
f.close()

head, body = splitheadbody(mb)
try:
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(StringIO.StringIO(head))
except ConfigParser.ParsingError:
	pass

validcodes = cfg.get('Description', 'UsedCodes')
d = {}
dd = {}
for line in body.splitlines():
	if not line.strip():
		continue
	p = 0
	for p in xrange(len(line)):
		if line[p] in validcodes:
			break
	assert line[p] in validcodes
	if p == 0: # in the form a XX XX XX
		ar = line.rstrip().split()
		if ar[0].startswith('`') and '`' not in validcodes:
			code = ar[0][1:]
		else:
			code = ar[0]
		assert code
		if not d.has_key(code):
			d[code] = []
		for s in ar[1:]:
			if s not in d[code]:
				d[code].append(s)
	else: # in the form XX a aaaa
		word = line[:p].rstrip()
		assert word
		ar = line[p:].strip().split()
		assert 0 < len(ar) <= 2
		if not dd.has_key(word):
			dd[word] = ar[-1]
		else:
			try:
				assert dd[word] == ar[-1]
			except:
				#print >>sys.stderr, enc(word), dd[word], ar[-1]
				pass
		code = ar[0]
		if not d.has_key(code):
			d[code] = []
		if word not in d[code]:
			d[code].append(word)
for word, code in dd.iteritems():
	if not d.has_key(code):
		d[code].append(word)
		print >> sys.stderr, enc(word), code

f = open(sys.argv[2], 'w')
print >> f, 'name=%s' % (enc(cfg.get('Description', 'Name')),)
print >> f, 'key=%s' % (cfg.get('Description', 'UsedCodes'),)
try:
	print >> f, 'len=%d' % (cfg.getint('Description', 'MaxCodes'),)
except ConfigParser.NoOptionError:
	pass
print >> f, 'wildcard=%s' % (cfg.get('Description', 'WildChar'),)
try:
	rules = []
	for k, v in cfg.items('Rule'):
		assert k[0] == 'c'
		assert k[1] in 'ae'
		assert k[2:].isdigit()
		rules.append((int(k[2:]), k[1], v))
	assert len(rules) == cfg.getint('Description', 'NumRules')
	rules.sort()
	for num, rel, rule in rules:
		print >> f, 'code_%s%d=%s' % (rel, num, rule)
except ConfigParser.NoSectionError:
	pass
print >> f, '[data]'
for code in sorted(d.iterkeys()):
	ar = [code]
	ar.extend(d[code])
	print >> f, enc(' '.join(ar))
f.close()

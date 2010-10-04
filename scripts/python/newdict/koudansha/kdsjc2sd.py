#!/usr/bin/env python
# -*- coding: sjis -*-
import sys, os.path, re
import unicodedata
import pdb

def charref2ustr(str):
	ar = str.decode('sjis').split('&#');
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s[0] != 'x':
			result.append(unichr(int(s[:p])))
		else:
			result.append(unichr(int(s[1:p], 16)))
		result.append(s[p+1:])
	return u''.join(result)

double = re.compile(r'【(.*?)】')
spanpat = re.compile(r'</?SPAN[^>]*>')
xmltag = re.compile(r'<.*?>')
enc = lambda s: s.encode('gb18030')

def gettitlepronun(line):
	if line.find('entryhilight') > 0:
		p = line.index('entryhilight>') + 13
		q = line.rindex('</SPAN>')
		line = line[p:q].rstrip()
	else:
		p = line.index('>')
		line = line[p+1:].rstrip()
	line = spanpat.sub('', line).replace('<SMALL>', '(').replace('</SMALL>'
			, ')')
	assert line.find('<') < 0
	p = line.find('【')
	if p >= 0:
		q = line.rfind('】')
		title = [s.strip() for s in charref2ustr(line[p+2:q]).split(
			u'・')]
		pronun = charref2ustr(line[:p]).strip()
	else:
		title = []
		pronun = charref2ustr(line).strip()
	assert pronun
	return title, pronun

totalresult = []
totaltitle = []
def flushitem(item):
	title = '|'.join([item[1]] + item[0])
	str = charref2ustr(''.join(item[2:]))
	str = str.replace('.bmp"', '.png"')
	try:
		stack = []
		ar = str.split('<')
		for s in ar[1:]:
			p = s.index('>')
			t = s[:p].split()[0]
			if t.startswith('/'):
				assert stack[-1] == t[1:]
				del stack[-1]
			elif t not in ('br', 'IMG'):
				stack.append(t)
		assert not stack
	except:
		print >> sys.stderr, title.encode('gb18030')
		print >> sys.stderr, str.encode('gb18030')
		print >> sys.stderr, stack, s.encode('gb18030')
		raise
	if str.endswith('<br>'):
		str = str[:-4]
	totalresult.append('%s\t%s\n' % (title, str))
	totaltitle.append(item[0] and item[0][0] or item[1])

annexpat = re.compile(ur'([0-9A-Za-z.．（）-]*<SPAN lang=zh>.*</SPAN>)([^<>]*)')

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s dump.htm' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

f = open(sys.argv[1], 'r')
state = 0
item = None
for line in f:
	if state == 0:
		if line.startswith('<DL>'):
			state = 1
	elif state == 1:
		assert line.startswith('<DT')
		try:
			title, pronun = gettitlepronun(line)
		except:
			print >> sys.stderr,charref2ustr(line).encode('gb18030')
			raise
		p = line.index('>')
		item = [title, pronun, line[p+1:].rstrip()+'<br>']
		state = 2
	elif state == 2:
		if line.startswith('<DT'):
			flushitem(item)
			try:
				title, pronun = gettitlepronun(line)
			except:
				print >> sys.stderr,charref2ustr(line).encode('gb18030')
				raise
			p = line.index('>')
			item = [title, pronun, line[p+1:].rstrip()+'<br>']
		elif line.startswith('</DD>') or line.startswith('</DL>'):
			flushitem(item)
			break
		elif line.startswith('<DD'):
			p = line.index('>')
			s = line[4:p]
			p += 1
			if s.endswith('example'):
				item.append('　　%s<br>' % (
						line[p:].rstrip(),))
			else:
				item.append(line[p:].rstrip() + '<br>')
		elif line == '<DIV></DIV>\n':
			item.append('<br>')
		elif line.startswith('<DIV'):
			assert line.startswith('<DIV class=')
			p = line.find('>')
			s = line[11:p]
			ll = line.rstrip()
			lp = line[:p+1]
			t = line[p+1:].rstrip()
			if s in ('tangocho', 'ruigigo', 'the', 'ito', 'tango'):
				item.append(ll)
				continue
			try:
				if not t.endswith('</DIV>'):
					assert s in 'subbody'
					assert not t
					state = 3
					item.append(ll)
					continue
			except:
				print >> sys.stderr, line
				raise
			if s == 'subtitle':
				item.append('<b>%s</b><br>' % (ll,))
			elif s.startswith('subbody'):
				item.append(ll + '<br>')
			elif s == 'example':
				item.append('%s　　%s<br>'% (lp, t,))
			else:
				print >> sys.stderr, 'Errrrrrr'
				pdb.set_trace()
	elif state == 3:
		s = line.rstrip()
		if s.endswith('</DIV></DIV>') or s.endswith('</TABLE></DIV>'):
			item.append('%s<br>' % (s,))
			state = 2
		else:
			item.append(s)
	else:
		print >> sys.stderr, 'Ooops'
		pdb.set_trace()
f.close()
result = ''.join(totalresult).encode('utf-8')
hrefpat = re.compile(r'<A href="#([^"]*)">')
result = hrefpat.sub(lambda m: '<A href="bword://%s">' % (totaltitle[int(
	m.group(1))].encode('utf-8'),), result)
result = spanpat.sub('', result)
sys.stdout.write(result)

#<IMG src="df_33.png">->(R01)
#<IMG src="df_34.png">->(R02)
#<IMG src="df_35.png">->(R03)
#<IMG src="df_36.png">->(R04)
#<IMG src="df_37.png">->(R05)
#<IMG src="df_38.png">->(R06)
#<IMG src="df_39.png">->(R07)
#<IMG src="df_40.png">->(R08)
#<IMG src="df_41.png">->(R09)
#<IMG src="df_42.png">->(R10)
#<IMG src="df_43.png">->(R11)
#<IMG src="df_44.png">->(R12)
#<IMG src="df_45.png">->(R13)
#<IMG src="df_46.png">->(R14)
#<IMG src="df_47.png">->(R15)
#<IMG src="df_48.png">->(R16)
#<IMG src="df_49.png">->(R17)
#<IMG src="df_50.png">->(R18)
#<IMG src="df_51.png">->(R19)
#<IMG src="df_52.png">->(R20)
#<IMG src="df_53.png">->(R21)
#<IMG src="df_54.png">->(R22)
#<IMG src="df_55.png">->(R23)
#<IMG src="df_56.png">->(R24)
#<IMG src="df_57.png">->(R25)
#<IMG src="df_58.png">->(R26)
#<IMG src="df_59.png">->(R27)
#<IMG src="df_60.png">->(R28)
#<IMG src="df_61.png">->(R29)
#<IMG src="df_62.png">->(R30)
#<IMG src="df_63.png">->(R31)
#<IMG src="df_64.png">->(R32)
#<IMG src="df_65.png">->(R33)
#<IMG src="df_66.png">->(R34)
#<IMG src="df_67.png">->(R35)
#<IMG src="df_68.png">->(R36)
#<IMG src="df_69.png">->(R37)
#<IMG src="df_70.png">->(R38)
#<IMG src="df_71.png">->(R39)
#<IMG src="df_72.png">->(R40)
#<IMG src="df_73.png">->(R41)
#<IMG src="df_74.png">->(R42)
#<IMG src="df_75.png">->(R43)
#<IMG src="df_76.png">->(R44)
#<IMG src="df_77.png">->(R45)
#<IMG src="df_78.png">->(R46)

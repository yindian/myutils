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

entitymap = {
161:	'&iexcl;',
162:	'&cent;',
163:	'&pound;',
164:	'&curren;',
165:	'&yen;',
166:	'&brvbar;',
167:	'&sect;',
168:	'&uml;',
169:	'&copy;',
170:	'&ordf;',
171:	'&laquo;',
172:	'&not;',
173:	'&shy;',
174:	'&reg;',
175:	'&macr;',
176:	'&deg;',
177:	'&plusmn;',
178:	'&sup2;',
179:	'&sup3;',
180:	'&acute;',
181:	'&micro;',
182:	'&para;',
183:	'&middot;',
184:	'&cedil;',
185:	'&sup1;',
186:	'&ordm;',
187:	'&raquo;',
188:	'&frac14;',
189:	'&frac12;',
190:	'&frac34;',
191:	'&iquest;',
192:	'&Agrave;',
193:	'&Aacute;',
194:	'&Acirc;',
195:	'&Atilde;',
196:	'&Auml;',
197:	'&Aring;',
198:	'&AElig;',
199:	'&Ccedil;',
200:	'&Egrave;',
201:	'&Eacute;',
202:	'&Ecirc;',
203:	'&Euml;',
204:	'&Igrave;',
205:	'&Iacute;',
206:	'&Icirc;',
207:	'&Iuml;',
208:	'&ETH;',
209:	'&Ntilde;',
210:	'&Ograve;',
211:	'&Oacute;',
212:	'&Ocirc;',
213:	'&Otilde;',
214:	'&Ouml;',
215:	'&times;',
216:	'&Oslash;',
217:	'&Ugrave;',
218:	'&Uacute;',
219:	'&Ucirc;',
220:	'&Uuml;',
221:	'&Yacute;',
222:	'&THORN;',
223:	'&szlig;',
224:	'&agrave;',
225:	'&aacute;',
226:	'&acirc;',
227:	'&atilde;',
228:	'&auml;',
229:	'&aring;',
230:	'&aelig;',
231:	'&ccedil;',
232:	'&egrave;',
233:	'&eacute;',
234:	'&ecirc;',
235:	'&euml;',
236:	'&igrave;',
237:	'&iacute;',
238:	'&icirc;',
239:	'&iuml;',
240:	'&eth;',
241:	'&ntilde;',
242:	'&ograve;',
243:	'&oacute;',
244:	'&ocirc;',
245:	'&otilde;',
246:	'&ouml;',
247:	'&divide;',
248:	'&oslash;',
249:	'&ugrave;',
250:	'&uacute;',
251:	'&ucirc;',
252:	'&uuml;',
253:	'&yacute;',
254:	'&thorn;',
255:	'&yuml;',
}
def fixentity(str):
	ar = str.split('&#');
	result = [ar[0]]
	for s in ar[1:]:
		p = s.index(';')
		if s[0] != 'x':
			code = int(s[:p])
		else:
			code = int(s[1:p], 16)
		result.append(entitymap.get(code, '&' + s[:p+1]))
		result.append(s[p+1:])
	return ''.join(result)

def pinyin2ascii(str):
	str = unicodedata.normalize('NFD', str)
	return ''.join(filter(lambda c: c.isalpha(), str)).encode('ascii')

def gaiji(str):
	result = []
	for c in str:
		try:
			c.encode('sjis')
		except UnicodeEncodeError:
			result.append('%04X' % (ord(c),))
		else:
			result.append(c)
	return ''.join(result).encode('sjis')

def gaijialt(str):
	result = []
	for c in str:
		try:
			c.encode('sjis')
		except UnicodeEncodeError:
			if altmap.has_key(ord(c)):
				result.append(altmap[ord(c)])
			else:
				result.append('%04X' % (ord(c),))
		else:
			result.append(c)
	return ''.join(result).encode('sjis')

double = re.compile(r'【(.*?)】')
zhspan = re.compile(r'<SPAN lang=zh>(.*?)</SPAN>')
xmltag = re.compile(r'<.*?>')
enc = lambda s: s.encode('gb18030')

def gettitlepronun(line):
	title = map(charref2ustr, zhspan.findall(line))
	if not title:
		title = map(charref2ustr, double.findall(line))
	if line.find('<', 1) < 0:
		assert not title
		title  = [charref2ustr(line[line.find('>')+1:].strip())]
	assert title or line.find('〓') > 0
	title = [xmltag.sub('', s) for s in title]
	p = line.rfind('</SPAN>')
	q = -1
	if line.find('entryhilight') > 0:
		q = p
		p = line.rfind('</SPAN>', 0, p)
	if p > 0:
		pronun = charref2ustr(line[p + len('</SPAN>'):q])
		pronun = xmltag.sub('', pronun).strip()
		pronun = pinyin2ascii(pronun)
	else:
		pronun = ''
	return title, pronun

def printtitle(title):
	for s in title:
		print '<key type="表記">%s</key>' % (gaiji(s),)
		if gaiji(s) != gaijialt(s):
			print '<key type="表記">%s</key>'%(gaijialt(s),)

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s dump.htm' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

try:
	f = open(os.path.join(os.path.dirname(sys.argv[0]), 'alternate.ini'),
			'r')
except:
	altmap = {}
	f.close()
else:
	altmap = {}
	for line in f:
		line = line.strip()
		if not line.startswith('u'):
			continue
		ar = line.split()
		assert len(ar) >= 2
		code = int(ar[0][1:], 16)
		altmap[code] = ar[1].decode('sjis')
	f.close()

print """\
<html>
<head>
<meta http-equiv="Content-Type" charset="Shift_JIS">
<title></title>
</head>
<body>"""

f = open(sys.argv[1], 'r')
state = 0
for line in f:
	if state == 0:
		if line.startswith('<DL>'):
			state = 1
	elif state == 1:
		assert line.startswith('<DT')
		print '<DL>'
		title, pronun = gettitlepronun(line)
		line = fixentity(line)
		print line + '</DT>'
		printtitle(title)
		print '<key type="表記">%s</key>' % (pronun,)
		print >> sys.stderr, enc(' | '.join(title)), '|', enc(pronun)
		print '<DD>'
		state = 2
	elif state == 2:
		if line.startswith('<DT'):
			print '</DD>'
			print '</DL>'
			print '<DL>'
			title, pronun = gettitlepronun(line)
			line = fixentity(line)
			print line + '</DT>'
			printtitle(title)
			print '<key type="表記">%s</key>' % (pronun,)
			print >> sys.stderr, enc(' | '.join(title)), '|', enc(pronun)
			print '<DD>'
		elif line.startswith('</DD>') or line.startswith('</DL>'):
			print '</DD>'
			print '</DL>'
			break
		elif line.startswith('<DD'):
			line = fixentity(line)
			p = line.index('>')
			s = line[4:p]
			p += 1
			if s.endswith('example'):
				print '<indent val=2>¶<indent val=3>%s<indent val=1><br>' % (
						line[p:].rstrip(),)
			else:
				#s = line[p:].rstrip()
				#if s: print '%s<br>' % (s,)
				s = t = line[p:].rstrip()
				if not s: continue
				if s.startswith('［'):
					t = t[:2] + '<indent val=2>' + t[2:]
				elif s.startswith('<B>'):
					p = t.find('</B>')
					assert p > 0
					p += 4
					t = t[:p] + '<indent val=2>' + t[p:]
				if t != s:
					print '%s<indent val=1><br>' % (t,)
				else:
					print '%s<br>' % (s,)
		elif line == '<DIV></DIV>\n':
			print '<p></p>'
		elif line.startswith('<DIV'):
			line = fixentity(line)
			assert line.startswith('<DIV class=')
			p = line.find('>')
			s = line[11:p]
			ll = line.rstrip()
			lp = line[:p+1]
			t = line[p+1:].rstrip()
			if s in ('tangocho', 'ruigigo'):
				#print '<p></p>'
				print ll
				continue
			try:
				if not t.endswith('</DIV>'):
					assert s == 'subbody'
					assert not t
					state = 3
					print ll
					continue
			except:
				print >> sys.stderr, line
				raise
			#t = t[:-6]
			#if t.endswith('</DIV>'):
			#	t = t[:-6]
			if s == 'subtitle':
				print '<b>%s</b><br>' % (ll,)
			elif s == 'subbody':
				p = 0
				while p < len(t) and t[p] == '<':
					p = t.find('>', p)
					if p < 0:
						break
					p += 1
				if p < len(t):
					if ord(t[p]) >= 0x80 and \
						(not 0xA1 <= ord(t[p]) <= 0xDF):
						p += 2
					elif t[p] == '&':
						p = t.find(';', p)
						assert p > 0
						p += 1
					else:
						p += 1
					t = t[:p] + '<indent val=2>' + t[p:]
				else:
					print >> sys.stderr, 'Errrr'
					pdb.set_trace()

				print '%s%s<indent val=1><br>' % (lp, t,)
			elif s == 'example':
				print '%s<indent val=2>¶<indent val=3>%s<indent val=1><br>' % (
						lp, t,)
			else:
				print >> sys.stderr, 'Errrrrrr'
				pdb.set_trace()
	elif state == 3:
		line = fixentity(line)
		s = line.rstrip()
		if s.endswith('</DIV></DIV>'):
			#print s[:-12]
			print '%s<br>' % (s,)
			state = 2
		else:
			print s
	else:
		print >> sys.stderr, 'Ooops'
		pdb.set_trace()
f.close()

print """\
</body>
</html>"""

#!/usr/bin/env python
import sys
import os
import re

try:
	out = sys.stdout.buffer
except AttributeError:
	out = sys.stdout

lnkpat = re.compile(br'''(<a +[^>]*\bhref=['"])([^'">]*)(?=['"][^>]*>)''', re.I)
imgpat = re.compile(br'''(<img +[^>]\bsrc=['"])([^'">]*)(?=['"][^>]*>)''', re.I)

def lnkconvmd2st(m):
	s = m.group(2)
	if s.startswith(b'entry:'):
		return b''.join((m.group(1), b'bword:', s[6:]))
	return m.group(1) + s

def imgconvmd2st(m):
	s = m.group(2)
	if s.startswith(b'file:'):
		s = s[5:]
	return m.group(1) + s.lstrip(b'/')

def convmd2st(fname):
	with open(fname, 'rb') as f:
		bom = f.read(2)
		if bom in (b'\xff\xfe', b'\xfe\xff'):
			raise Exception('encoding not supported')
	cssfn = os.path.splitext(fname)[0] + '.css'
	rules = {}
	if os.path.exists(cssfn):
		with open(cssfn, 'rb') as f:
			k = b = a = None
			for line in f:
				if k is None:
					k = int(line)
				elif b is None:
					b = line.rstrip(b'\r\n')
				else:
					a = line.rstrip(b'\r\n')
					rules[k] = (b, a)
					k = b = a = None
	ar = []
	syn = {}
	k = v = None
	with open(fname, 'rb') as f:
		no = 0
		for line in f:
			no += 1
			try:
				if k is None:
					k = line.rstrip(b'\r\n')
					v = []
				elif line.startswith(b'</>'):
					assert len(line.rstrip()) == 3
					v = b'\n'.join(v)
					if v.startswith(b'@@@LINK='):
						assert v.find(b'\n') < 0
						syn.setdefault(v[8:], []).append(k)
					else:
						br = v.split(b'`')
						b = a = None
						for i in range(1, len(br), 2):
							s = a or b''
							try:
								n = int(br[i])
								b, a = rules[n]
							except:
								print('i = %d' % (i,))
								raise
							br[i] = s + b
						v = b''.join(br)
						v = lnkpat.sub(lnkconvmd2st, v)
						v = imgpat.sub(imgconvmd2st, v)
						v = v.replace(b'\\n', b'\\\n').replace(b'\n', b'\\n')
						ar.append((k, v))
					k = v = None
				else:
					v.append(line.rstrip(b'\r\n'))
			except:
				print('Error on line %d' % (no,))
				raise
	assert k is None and v is None
	out.writelines([b'%s\t%s\n' % (b'|'.join([k] + syn.get(k, [])), v) for k, v in ar])

def lnkconvst2md(m):
	s = m.group(2)
	if s.startswith(b'bword:'):
		return b''.join((m.group(1), b'entry:', s[6:]))
	return m.group(1) + s

def imgconvst2md(m):
	s = m.group(2)
	if not s.startswith(b'file:'):
		s = b'file://' + s
	return m.group(1) + s

def convst2md(fname):
	with open(fname, 'rb') as f:
		no = 0
		for line in f:
			no += 1
			try:
				k, v = line.rstrip(b'\r\n').split(b'\t', 1)
				v = v.replace(b'\\n', b'\n').replace(b'\\\n', b'\\n')
				v = lnkpat.sub(lnkconvst2md, v)
				v = imgpat.sub(imgconvst2md, v)
				if k.find(b'|') < 0:
					out.write(b'%s\n%s\n</>\n' % (k, v))
				else:
					ar = k.split(b'|')
					k = ar[0]
					out.write(b'%s\n%s\n</>\n' % (k, v))
					for s in ar[1:]:
						out.write(b'%s\n@@@LINK=%s\n</>\n' % (s, k))
			except:
				print('Error on line %d' % (no,))
				raise

if __name__ == '__main__':
	if sys.argv[1] != '-r':
		for fname in sys.argv[1:]:
			convmd2st(fname)
	else:
		for fname in sys.argv[2:]:
			convst2md(fname)

#!/usr/bin/env python
import sys

fields = []
widths = {}
repo = {}

def add_glyph(line):
	ar = map(str.strip, s.split('|'))
	d = {}
	for i in range(1, len(ar)):
		d[fields[i]] = ar[i]
	repo[ar[0]] = d

def calc_strokes(k):
	try:
		d = repo[k]
	except KeyError:
		d = repo[k[:k.index('@')]]
	x = d.get('strokes')
	if x:
		return x
	ar = d[fields[-1]].split('$')
	x = 0
	d['strokes'] = -1
	for s in ar:
		if len(s) < 2:
			continue
		try:
			n = int(s[:s.index(':')])
			if n % 100 == 99:
				br = s.split(':')
				try:
					n = calc_strokes(br[7])
				except (KeyError, ValueError):
					n = -1
				if n > 0:
					x += n
				else:
					d['strokes'] = -1
					return -1
			else:
				x += 1
		except:
			sys.stderr.write('k=%s, s=%s, ar=%s\n' % (k, s, ar))
			d['strokes'] = -1
			return -1
	if x == 0:
		x = -1
	d['strokes'] = x
	return x

def dump_repo(f=sys.stdout):
	print('|'.join([s.center(widths[s]) for s in fields]))
	print('+'.join(['-' * widths[s] for s in fields]))
	w0 = widths[fields[0]]
	for k in sorted(repo.keys()):
		f.write(' ')
		f.write(k.ljust(w0 - 1))
		f.write('|')
		for s in fields[1:-1]:
			f.write(' ')
			f.write(str(repo[k][s]).ljust(widths[s] - 1))
			f.write('|')
		f.write(' ')
		f.write(repo[k][fields[-1]])
		f.write('\n')

if __name__ == '__main__':
	with open(sys.argv[1]) as f:
		s = f.readline()
		fields.extend(map(str.strip, s.split('|')))
		s = f.readline()
		ar = s.split('+')
		assert len(ar) == len(fields)
		for i in range(len(ar)):
			widths[fields[i]] = ar[i].count('-')
		for s in f:
			if s.startswith('('):
				break
			add_glyph(s)
		fields.insert(2, 'strokes')
		widths['strokes'] = 9
		for k in repo.keys():
			calc_strokes(k)
		dump_repo()
		print(s)

import sys
buf = []
title = []
state = 0
for line in sys.stdin:
	if state == 0:
		if line.startswith('<dd><p>'):
			state = 1
			buf = [line]
			if title:
				sys.stdout.write('|'.join(title))
				sys.stdout.write('\t')
				title = []
		else:
			if line.startswith('<dt') or line.startswith('<key'):
				p = line.index('>') + 1
				q = line.rindex('<')
				title.append(line[p:q])
			else:
				sys.stdout.write(line)
	elif state == 1:
		buf.append(line)
		if line.startswith('</p></dd>'):
			state = 0
			sys.stdout.write(''.join(buf).replace('\n', ''))
			sys.stdout.write('\n')
			buf = []
if buf:
	sys.stdout.write(''.join(buf).replace('\n', ''))
	sys.stdout.write('\n')

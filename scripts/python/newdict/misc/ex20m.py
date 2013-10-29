#!/usr/bin/env python
import glob
fl = glob.glob('*.csv')
fl.sort()
fl = fl[:1] + fl[6:10] + fl[1:6] + fl[10:]

BUFSIZE = 1024**2 * 2

sel = [x-1 for x in [1,4,5,6,7,8,20,23,24,32]]
last = None
for fn in fl:
	f = open(fn, 'rb')
	lineno = 0
	sepnum = 0
	buf = f.read(BUFSIZE)
	while buf:
		lines = buf.split('\r\n')
		if lineno == 0:
			sepnum = lines[0].count(',')
			del lines[0]
		i = len(lines) - 2
		while i >= 0:
			c = lines[i].count(',')
			if c < sepnum:
				assert i > 0
				lines[i-1] += ' ' + lines[i]
				del lines[i]
			else:
				assert c >= sepnum
			i -= 1
		if lines[0] == last:
			del lines[0]
		if lines:
			lineno += len(lines) - 1
			if len(lines) > 1:
				last = lines[-2]
			buf = lines[-1] + f.read(BUFSIZE)
			del lines[-1]
			fieldnum = sepnum + 1
			for line in lines:
				ar = line.split(',')
				try:
					if len(ar) > fieldnum:
						i = 0
						while i < len(ar):
							if ar[i].startswith('"'):
								while ar[i].count('"') % 2:
									while not ar[i+1].endswith('"'):
										ar[i] += ',' + ar[i+1]
										del ar[i+1]
									ar[i] += ',' + ar[i+1]
									del ar[i+1]
								assert ar[i].endswith('"')
								#ar[i] = ar[i][1:-1]
							i += 1
					assert len(ar) == fieldnum
					print ','.join(map(ar.__getitem__, sel))
				except:
					print line
					print len(ar), fieldnum, ar
					raise
		else:
			buf = ''
	f.close()
	try:
		assert lineno in (1999999, 2000000, 50145)
	except:
		print fn, lineno

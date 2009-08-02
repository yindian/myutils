#!/usr/bin/env python
import sys, re

deltag = re.compile('<[^>]*>')

def addtowordlist(wordlist, ar):
	s = ' '.join(ar[1:])
	s = deltag.sub('', s)
	p = 0
	try:
		while 'A' <= s[p] <= 'Z':
			p += 1
		assert p == 1 or p == 2
		while '0' <= s[p] <= '9':
			p += 1
		assert p == 5 or p == 6
		if s[p] == 'A' or s[p] == 'B':
			p += 1
	except:
		print >> sys.stderr, p, s
		raise
	s = s[p:].replace(' ', '')
	#s = s[p:].strip()
	#print s
	wordlist.append(s)

assert __name__ == '__main__'
assert len(sys.argv) == 2
f = open(sys.argv[1], 'r')
buf = f.read()
f.close()
ar = buf.split('<a id=')[2:]
ar = [s[s.index('>')+1:] for s in ar]
k = ord('A')
for i in range(26-3):
	assert ar[i].startswith(chr(k))
	while True:
		k += 1
		if chr(k) not in 'IUV':
			break
assert ar[26-3].startswith('ZF')

wordlist = []
for i in range(26-3+1):
	lines = ar[i].split('<br>\n')
	# special treatment
	if lines[0].find('ZF0001') > 0:
		lines[0] = lines[0][lines[0].index('1 <font'):]
	lastnum = 0
	for line in lines:
		line = line.split()
		if len(line) >= 2 and line[-1] != 'Title' and \
				not line[-1].startswith('Top') and \
				not line[-1].startswith('style'):
			try:
				num = int(line[0])
			except:
				print >> sys.stderr, line
				raise
			try:
				assert num == lastnum + 1
			except:
				print >> sys.stderr, line
				print >> sys.stderr, lastnum, num
				raise
			lastnum = num
			addtowordlist(wordlist, line)
i = 26-3+1 # zwdsnb
lines = ar[i].split('<br>\n')
wordlist.insert(0, lines[0].strip())

k = lastnomatch = 0
meanlist = {}
for i in range(26-3+1, len(ar)-1):
	lines = ar[i].split('<br>\n')
	word = lines[0].replace(' ', '')
	try:
		assert word == wordlist[k]
		meanlist[k] = '\n'.join(lines[1:]).strip()
	except:
		print >> sys.stderr, '|%s| != |%s|' % (lines[0], wordlist[k])
		if word == wordlist[k+1]:
			lastnomatch = k
			k += 1
			meanlist[k] = '\n'.join(lines[1:]).strip()
			pass
		elif word == wordlist[lastnomatch]:
			meanlist[lastnomatch] = '\n'.join(lines[1:]).strip()
			lastnomatch = 0
			k -= 1
			pass
		else:
			raise
	k += 1

assert lastnomatch == 0
i = len(ar)-1
lines = ar[i].split('<br>\n')
word = lines[0].replace(' ', '')
assert word == wordlist[k]
p = 1
while True:
	line = lines[p].replace(' ', '')
	if line.endswith(wordlist[k+1]):
		break
	elif k < len(wordlist)-2 and line.endswith(wordlist[k+2]):
		lastnomatch = k+1
		break
	p += 1
if lastnomatch == 0:
	lastline = lines[p][:-len(wordlist[k+1])]
else:
	lastline = lines[p][:-len(wordlist[lastnomatch])]
meanlist[k] = '\n'.join(lines[1:p] + [lastline]).strip()

#print wordlist[k], meanlist[k]

if lastnomatch == 0:
	k += 1
else:
	k += 2

i = p + 1
lastk = k
while i < len(lines) and k < len(wordlist) - 1:
	p = i
	kk = -1
	while True:
		line = lines[p].replace(' ', '')
		if line.endswith(wordlist[k+1]):
			kk = k+1
			break
		elif lastnomatch != 0 and line.endswith(wordlist[lastnomatch]):
			kk = lastnomatch
			print >> sys.stderr, 'Match |%s|' % (wordlist[kk],)
			break
		elif lastnomatch == 0 and k < len(wordlist)-2 and \
				line.endswith(wordlist[k+2]):
			print >> sys.stderr, 'No match |%s|' % (wordlist[k+1],)
			lastnomatch = k+1
			kk = k+2
			break
		p += 1
		if p - i >= 1000:
			print >> sys.stderr, lines[i]
			print >> sys.stderr, wordlist[k]
			raise Exception('fail')
	if lastnomatch == 0:
		lastline = lines[p][:-len(wordlist[k+1])]
	else:
		lastline = lines[p][:-len(wordlist[lastnomatch])]
	meanlist[lastk] = '\n'.join(lines[i:p] + [lastline]).strip()
	if kk > k:
		lastk = k = kk
	else:
		lastk = kk
		lastnomatch = 0
	i = p+1

lines[-1] = deltag.sub('', lines[-1])
meanlist[k] = '\n'.join(lines[i:]).strip()

for i in range(len(wordlist)):
	print wordlist[i]
	print meanlist[i]
	print '</>'

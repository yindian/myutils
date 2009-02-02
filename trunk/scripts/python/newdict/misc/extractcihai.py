#!/usr/bin/env python
import sys

tag1 = '\x1f\x1f'
tag2 = '\x1e\x1e'
tag3 = '\x1d\x1d'
rubbish = '\xaa\xa6\x1a'

if __name__ == '__main__':
	assert len(sys.argv) > 1
	str = open(sys.argv[1], 'rb').read()
	strlen = len(str)
	pos = str.find(tag1)
	if pos < 0:
		pos = None
	while pos and pos < strlen:
		assert str[pos:pos+2] == tag1
		pos2 = str.find(tag2, pos)
		pos3 = str.find(tag3, pos)
		pos4 = str.find(tag1, pos+2)
		assert pos < pos2 < pos3
		if pos4 < 0:
			pos4 = None
		word = str[pos+2:pos2]
		read = str[pos2+2:pos3]
		mean = str[pos3+2:pos4]
		word = word[0] + chr(ord(word[1])+21) + word[2:]
		read = read[0] + chr(ord(read[1])+20) + read[2:]
		mean = mean[0] + chr(ord(mean[1])+19) + mean[2:]
		if mean.find(rubbish) > 0:
			mean = mean.replace(rubbish, '')
		print '%s\t%s\\n%s' % (word, read, mean)
		pos = pos4

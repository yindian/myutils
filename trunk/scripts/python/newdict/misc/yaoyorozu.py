#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string
import libxml2dom
from libxml2dom import Node

assert __name__ == '__main__'

for idx in range(27, 47):
	fname = 'test%d.html' % idx
	document = libxml2dom.parseString(open(fname, 'r').read(), html=1,
			htmlencoding='euc-jp');
	title = document.getElementsByTagName('i')
	if not title:
		document = libxml2dom.parseString(open(fname, 'r').read(),
				html=1, htmlencoding='sjis');
		title = document.getElementsByTagName('i')
	assert len(title) == 1
	title = title[0].textContent

	for tr in document.getElementsByTagName('tr'):
		if not tr.childNodes:
			continue
		th = td = None
		for sub in tr.childNodes:
			if sub.nodeName == 'th':
				th = sub.textContent
			elif sub.nodeName == 'td':
				td = sub.textContent
		assert th is not None and td is not None
		if not th and not td:
			continue
		sys.stdout.write(th.encode('utf-8'))
		sys.stdout.write('\t')
		sys.stdout.write(title.encode('utf-8'))
		sys.stdout.write('\\n')
		sys.stdout.write(td.replace('\n', '').encode('utf-8'))
		sys.stdout.write('\n')

#!/usr/bin/env python3
import bs4
try:
	from urllib.parse import unquote
except:
	from urllib import unquote
import sys
import os.path
import traceback

def print_list_from_index_html(path, out=sys.stdout):
	if os.path.isdir(path) or path.endswith('/'):
		path = os.path.join(path, 'index.html')
	try:
		f = open(path)
	except FileNotFoundError:
		raise
	html = bs4.BeautifulSoup(f, features='html.parser')
	f.close()
	path = os.path.dirname(path)
	for tag in html.find_all('a'):
		href = tag.get('href')
		if not href or href[0] == '#' or href in ('..', '.'):
			continue
		if type(href) != str:
			href = href.encode('utf-8')
		href = unquote(href)
		if href.endswith('/'):
			if href.startswith('../') or href == './':
				continue
			try:
				print_list_from_index_html(os.path.join(path, href), out)
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc()
		else:
			out.write(os.path.join(path, href))
			out.write('\n')

if __name__ == '__main__':
	path = sys.argv[1]
	print_list_from_index_html(path)

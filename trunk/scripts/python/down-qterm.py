# coded by Yin Dian on 08.4.16-17.
import qterm
import sys, time, os, string, re

lastlineno = 23
bbsencoding = 'gbk'
filenameenc = 'utf-8'
sep = '.'
colorful = True
maxtry = 20

def nameconv(str):
	return unicode(str, bbsencoding, 'ignore').encode(filenameenc,
			'ignore').replace('/', '_').replace("\\", '_')

def small_sleep():
	time.sleep(0.1)

def wait_until_stable(lp):
	xpos = qterm.caretX(lp)
	ypos = qterm.caretY(lp)
	small_sleep()
	x = qterm.caretX(lp)
	y = qterm.caretY(lp)
	while x != xpos or y != ypos:
		xpos = x
		ypos = y
		small_sleep()
		x = qterm.caretX(lp)
		y = qterm.caretY(lp)

def wait_until_change(lp):
	xpos = qterm.caretX(lp)
	ypos = qterm.caretY(lp)
	line = qterm.getText(lp, ypos)
	small_sleep()
	x = qterm.caretX(lp)
	y = qterm.caretY(lp)
	str = qterm.getText(lp, y)
	t = maxtry
	while x == xpos and y == ypos and str == line and t > 0:
		small_sleep()
		x = qterm.caretX(lp)
		y = qterm.caretY(lp)
		str = qterm.getText(lp, y)
		t -= 1

def send_char(lp, ch):
	qterm.sendString(lp, ch)
	print 'send', ch
	wait_until_change(lp)
	wait_until_stable(lp)

def return_to_list(lp):
	lineno = qterm.caretY(lp)
	if lineno == lastlineno:	# already in article mode
		send_char(lp, 'q')
		if qterm.caretY(lp) == lastlineno:	# still in article mode, press q again
			send_char(lp, 'q')
		if qterm.caretY(lp) == lastlineno:	# still in article mode, not expected
			return False
	elif lineno < 3:	# in reply or post mode
		return False
	return True

def get_title_list_ready(lp):
	global lastlineno
	if not return_to_list(lp):
		return
	lineno = qterm.caretY(lp)
	line = qterm.getText(lp, lineno)
	# try digest list
	exp = r'^(?:->|\s*>)\s*(\d+)\s*\[(.+?)\]\s*(.*?)\s*$'
	matchobj = re.match(exp, line)
	if matchobj:
		return 1, matchobj.group(1), matchobj.group(2), matchobj.group(3)
	else:	# try normal article list
		exp = r'^(?:>)\s*(\S+)\s*(?:[+*NmMgGbBrRoO.])?\s+(\S+)\s*(\w+)\s*(\d+)(?:\.)?\s*(?:x|@)?(¡ñ|¡ô|¡ï|Re:|©À) (.*?)\s*$'
		print 'maybe article'
		matchobj = re.match(exp, line)
		if matchobj:
			if matchobj.group(5) == 'Re:' or matchobj.group(5) == '©À':
				reply = 'Re: '
			else:
				reply = ''
			return 0, matchobj.group(1), matchobj.group(2), reply + matchobj.group(6)
		else:
			print 'line %s not matched' % line

def strip_digest_title_date_bm(str):
	exp = r'^(.*?)\s*(\(BM:.*?\))?\s*\[?\s*(\d+[-.]\d+[-.]\d+[-.]?)\s*\]?\s*$'
	matchobj = re.match(exp, str)
	if matchobj:
		return matchobj.group(1)
	else:
		return str

def purge_ansi(str):
	lines = str.split('\n')
	for i in range(len(lines)):
		if lines[i].startswith('\033\033[37;40m') and lines[i].endswith('\033\033[0m'):
			str2 = lines[i][9:-5]
			if str2.find('\033') < 0:
				lines[i] = str2
	return '\n'.join(lines)

def down_digest(lp, dir):
	if dir[-1] != '/':
		dir += '/'
	if not os.access(dir, os.F_OK):
		os.makedirs(dir)
	title = get_title_list_ready(lp)
	if not title:
		return
	if title[0] != 1:
		raise 'Not in Digest mode'
	initnum = title[1]
	while True:
		if title[2] != 'Ä¿Â¼':
			send_char(lp, 'r')
			text = qterm.copyArticle(lp, colorful)
			return_to_list(lp)
			f = open(dir + nameconv(title[1] + sep + 
				strip_digest_title_date_bm(title[3])), 'w')
			f.write(purge_ansi(text))
			f.close()
		else:
			send_char(lp, 'r')
			down_digest(lp, dir + nameconv(title[1] + sep + 
				strip_digest_title_date_bm(title[3])))
			send_char(lp, 'q')
		send_char(lp, 'j')
		title = get_title_list_ready(lp)
		if title[1] == initnum:
			break

def down_article(lp, dir):
	if dir[-1] != '/':
		dir += '/'
	if not os.access(dir, os.F_OK):
		os.makedirs(dir)
	title = get_title_list_ready(lp)
	if not title:
		return
	if title[0] != 0:
		raise 'Not in Article mode'
	initnum = title[1]
	while True:
		send_char(lp, 'r')
		text = qterm.copyArticle(lp, colorful)
		return_to_list(lp)
		f = open(dir + nameconv(title[1] + sep + title[3]), 'w')
		f.write(purge_ansi(text))
		f.close()
		send_char(lp, 'j')
		title = get_title_list_ready(lp)
		if title[1] == initnum:
			break

lp = long(sys.argv[0])
lastlineno = qterm.rows(lp)-1

	

#destdir = os.environ['HOME']+"/.qterm/downloads/"+time.ctime()+"/"
destdir = os.environ['HOME']+"/linshi/qterm/download/" + time.ctime()
if not os.access(destdir, os.F_OK):
	os.makedirs(destdir)

sys.stdout = open(destdir+".log", "w")


inittitle = get_title_list_ready(lp)

if inittitle:
	if inittitle[0] == 1:
		down_digest(lp, destdir)
	else:
		down_article(lp, destdir)
else:
	print "Error: could not get title."

sys.stdout.flush()
sys.stdout.close()

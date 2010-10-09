#!/usr/bin/env python
import sys, os.path, time
import win32com, win32com.client, win32gui, win32con, pythoncom
import win32clipboard, win32ui, win32api
import ImageGrab
import pdb, traceback

def fnquote(str):
	return str.replace(':', '_')

enc = lambda s: s.encode('sjis', 'xmlcharrefreplace')

def writelines(lines, cr=True, outf=sys.stdout):
	if cr:
		for line in lines:
			print >> outf, line
	else:
		outf.writelines(lines)

def getIEServer(hwnd, ieServer):
	if win32gui.GetClassName(hwnd) == 'Internet Explorer_Server':
		ieServer.append(hwnd)

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print 'Usage: %s window_class_name' % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

mainHwnd = win32gui.FindWindow(sys.argv[1], None)
if not mainHwnd:
	print 'Class name %s not found.' % (sys.argv[1],)
	sys.exit(1)
ieServers = []
win32gui.EnumChildWindows(mainHwnd, getIEServer, ieServers)
if not ieServers:
	print 'IE server not found.'
	sys.exit(2)

ieServer = ieServers[0]
msg = win32gui.RegisterWindowMessage('WM_HTML_GETOBJECT')
ret, result = win32gui.SendMessageTimeout(ieServer, msg, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000)
ob = pythoncom.ObjectFromLresult(result, pythoncom.IID_IDispatch, 0)
doc = win32com.client.dynamic.Dispatch(ob)

win32gui.ShowWindow(mainHwnd,win32con.SW_MAXIMIZE)
win32gui.SetForegroundWindow(mainHwnd)
time.sleep(0.1)

wl,wt,r,b=win32gui.GetWindowRect(ieServer)

finished = False
lasthtml = None
loopcnt = 0
while not finished:
	loopcnt += 1
	html = doc.body.innerHTML
	prefix = html[:128]
	html = enc(html).splitlines()
	if not lasthtml:
		writelines(html[:-1])
	else:
		p = 1
		try:
			while lasthtml[-2] != html[p]:
				p += 1
		except:
			traceback.print_exc()
			pdb.set_trace()
		q = p - 1
		if q > 10: q = 10
		try:
			while lasthtml[-2-q:-2] != html[p-q:p]:
				p += 1
		except:
			traceback.print_exc()
			pdb.set_trace()
		writelines(html[p+1:-1])
		if p == len(html) - 1:
			writelines(html[-1:])
			break
	lasthtml = html
	if doc.images.length > 0:
		for item in doc.body.getElementsByTagName('img'):
			fname = fnquote(item.src) + '.bmp'
			if os.path.exists(fname):
				continue
			item.scrollIntoView()
			l = item.offsetLeft - item.offsetParent.scrollLeft
			t = item.offsetTop  - item.offsetParent.scrollTop
			w = item.offsetWidth
			h = item.offsetHeight
			l += wl
			t += wt
			time.sleep(0.05)
			win32api.keybd_event(win32con.VK_SNAPSHOT, 0)
			time.sleep(0.1)
			im = ImageGrab.grabclipboard()  
			im = im.crop((l, t, l+w, t+h))
			im.save(fname, "BMP")  
			print >> sys.stderr, fname, 'saved.'
	trycount = 0
	oldscrolltop = doc.body.scrollTop
	while doc.body.innerHTML.startswith(prefix):
		#doc.body.doScroll('scrollbarPageDown')
		win32api.keybd_event(win32con.VK_NEXT, 0)
		time.sleep(0.05)
		if doc.body.scrollTop == oldscrolltop:
			if trycount > 20:
				finished = True
				writelines(html[-1:])
				break
			time.sleep(0.05)
			trycount += 1
		else:
			oldscrolltop = doc.body.scrollTop
print >> sys.stderr, 'Done. %d loops.' % (loopcnt,)

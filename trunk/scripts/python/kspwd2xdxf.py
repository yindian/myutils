#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path, string, re
import zipfile, codecs
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
import pdb

def getdictinfo(dom):
	assert dom.tagName == u'dictionary_information'
	count = dom.getElementsByTagName(u'item_count')[0].firstChild.nodeValue
	count = int(count)
	dispinfo = dom.getElementsByTagName(u'display_information')[0]
	desc = dispinfo.getElementsByTagName(u'desc')
	k = 0
	for i in xrange(desc.length):
		cp = desc[i].getElementsByTagName(u'cp')[0].firstChild.nodeValue
		if cp == '936':
			k = i
			break
	name = desc[k].getElementsByTagName(u'name')[0].firstChild.nodeValue
	ar = ([desc[k].getElementsByTagName(u'class')[0].firstChild.nodeValue,
		desc[k].getElementsByTagName(u'description')[0
			].firstChild.nodeValue,
		desc[k].getElementsByTagName(u'copyright')[0
			].firstChild.nodeValue,
		u'\n',
		desc[0].getElementsByTagName(u'class')[0].firstChild.nodeValue,
		desc[0].getElementsByTagName(u'description')[0
			].firstChild.nodeValue,
		desc[0].getElementsByTagName(u'copyright')[0
			].firstChild.nodeValue,
		])
	if k == 0:
		del ar[len(ar)/2:]
	return count, name, u'\n'.join(ar)

cdatamarkupmap = {
		'B': 'b',
		'I': 'i',
		'U': 'kref',
		'+': 'sup',
		'-': 'sub',
		'L': 'iref',
		'x': 'tr',
		'l': 'iref',
		}
def cdataconv(str):
	"&B{粗体}, &I{斜体}, &U{下划线}, &+{上标}, &-{下标}, &L{链接}"
	ar = str.split('&')
	result = [ampquote(ar[0])]
	for s in ar[1:]:
		try:
			assert cdatamarkupmap.has_key(s[0])
			assert s[1] == '{'
		except:
			pdb.set_trace()
		try:
			p = s.index('}')
		except:
			result.append(s[2:])
			continue
		tag = cdatamarkupmap[s[0]]
		if tag == 'iref' and (s.find(':', 2, p) < 0 or s.count(
			'/', 2, p) + s.count('.', 2, p) + s.count('@', 2, p)
			< 2): # does not seems a URL
			tag = 'kref'
		result.append('<')
		result.append(tag)
		result.append('>')
		result.append(ampquote(s[2:p]))
		result.append('</')
		result.append(tag)
		result.append('>')
		result.append(ampquote(s[p+1:]))
		if not result[-1] and tag.endswith('ref'):
			result.append(' ')
	return ''.join(result)

dic_fmt={'YX':'<b>%s</b>', 'DX':'<b>%s</b>', #粗体
	 'JX':'* %s',                                    #列表
	 'RP':'<c c="orange">%s</c>',  #假名                                 #音标
	 'LY':'<blockquote><c c="red">%s</c></blockquote>',
	 'LS':'<blockquote><c c="blue">%s</c></blockquote>', 
	 }

dic_head = {'CY':U'基本词义',
	    'YF':U'用法',
	    'JC':U'继承用法',
	    'TS':U'特殊用法',
	    'XB':U'词性变化',
	    'PS':U'派生',
	    'YY':U'语源',
	    'XY':U'习惯用语',
	    'CC':U'参考词汇',
	    'CZ':U'常用词组'
	    }

def ck2article(dom):
	U"""
	In reference to zdictool.py
	&B{粗体}, &I{斜体}, &U{下划线}, &+{上标}, &-{下标}, &L{链接}
	CK:词库
	    DC:词头 生词本
	    JS:解释
		CY:基本词义
		YF:用法
		JC:继承用法
		TS:特殊用法
		XB:词性变化
		PS:派生
		YY:语源
		XY:习惯用语
		CC:参考词汇
		CZ:常用词组
		    CX:
			YX:原形*
			未使用之文本，DX
			DX:词性、说明 粗体
			    [infg:派生
				sy:单复数
				inf:后缀
			    sc:世纪
			    lg:
			    ge:]
			YJ:
			GZ:*
			OJ:又作
			YD:同形词 后带上标
			YB:音标
			    RP:日语假名
			    CB:音标
			    PY:拼音
			    TB:注音符号
			JX:* 列表
			GZ:
			LJ:* 蓝色缩进
			    LY:原
			    LS:释                    
			GT:
			    GY:原
			    GE:解
			XG:同义词
	"""
	result = []
	for node in dom.childNodes:
		if node.nodeType == node.CDATA_SECTION_NODE:
			data = cdataconv(node.data)
			if dom.tagName == 'DC':
				result.append('<k>')
				result.append(data)
				result.append('</k>')
			elif dom.tagName in dic_fmt:
				result.append(dic_fmt[dom.tagName] % (data,))
			else:
				result.append(data)
			if dom.tagName not in ['PY', 'TB', 'RP', 'CB']:
				result.append('\n')
		elif node.nodeType == node.ELEMENT_NODE:
			if node.tagName in dic_head:
				result.append(u'\n<c c="blue"><b>%s</b></c>\n'
						% (dic_head[node.tagName],))
			result.append(ck2article(node))
			if node.tagName == 'YB':
				result.append(u'\n')
	return u''.join(result)

def missingmatch(str):
	stack = []
	p = str.find('<')
	for s in str.split('<')[1:]:
		p = s.index('>')
		if s[0] == '!':
			pass
		elif s[0] == '/':
			assert s[1:p] == stack[-1]
			del stack[-1]
		else:
			stack.append(s[:p])
	stack.reverse()
	return ''.join(['\n</%s>' % (s,) for s in stack])

def fixmismatch(str):
	stack = []
	p = str.find('<')
	ar = str.split('<')
	result = [ar[0]]
	for s in ar[1:]:
		try:
			p = s.index('>')
		except:
			pdb.set_trace()
		if s[0] == '!':
			pass
		elif s[0] == '/':
			if s[1:p] != stack[-1]:
				# handle special case first
				if len(result) > 3 and (result[-1].startswith(
					'!')  and result[-3].startswith('!')):
					print >> sys.stderr, 'Special case'
					s = '/' + stack[-1] + s[p:]
					p = s.index('>')
			try:
				while s[1:p] != stack[-1]:
					result.append('</%s>\n' % (stack[-1],))
					del stack[-1]
			except:
				pdb.set_trace()
			del stack[-1]
		else:
			stack.append(s[:p])
		result.append('<')
		result.append(s)
	stack.reverse()
	result.extend(['\n</%s>' % (s,) for s in stack])
	return ''.join(result)

ampquote=lambda s:s.replace('&', '&amp;').replace('<', '&lt;').replace('>',
		'&gt;').replace("'", '&apos;').replace('"', '&quot;')
ampunquote=lambda s:s.replace('&quot;', '"').replace('&apos;', "'").replace(
		'&gt;'  , '>').replace('&lt;'  , '<').replace('&amp;' , '&')

assert __name__ == '__main__'

if len(sys.argv) < 2:
	print "Usage: %s [-t] filename.DIC.inf"
	sys.exit(0)

argv = sys.argv[1:]
if argv[0] == '-t':
	tabfileout = True
	del argv[0]
else:
	tabfileout = False
infile = argv[0]

def utf8write(str, outf=sys.stdout):
	outf.write(str.encode('utf-8'))

def utf8writeln(str, outf=sys.stdout):
	print >> outf, str.encode('utf-8')

f = codecs.open(os.path.splitext(infile)[0] + '.txt', 'rb', 'utf-16le')
assert f.read(1) == u'\ufeff'
zipf = zipfile.ZipFile(os.path.splitext(infile)[0] + '.zip', 'r')

if tabfileout:
	for line in f:
		word, fname = line.rstrip().split(u'\t', 1)
		mean = zipf.read(fname).decode('utf-16le')
		p = mean.startswith(u'\ufeff') and 1 or 0
		q = mean.endswith(u'\0') and -1 or len(mean)
		mean = mean[p:q].rstrip()
		utf8writeln('%s\t%s' % (word, mean.replace(u'\\n', u'\\\\n'
			).replace(u'\n', u'\\n')))
else:
	utf8writeln('''\
<?xml version="1.0" encoding="UTF-8" ?>
<xdxf lang_from="ENG" lang_to="ENG" format="visual">''')
	g = codecs.open(os.path.splitext(infile)[0] + '.inf', 'rb', 'utf-16le')
	assert g.read(1) == u'\ufeff'
	dom = parseString(g.read().rstrip(u'\0').encode('utf-8')).childNodes[0]
	g.close()
	itemcount, name, description = getdictinfo(dom)
	utf8writeln('<full_name>%s</full_name>' % (ampquote(name),))
	utf8writeln('<description>%s</description>' % (ampquote(description),))
	wordcount = 0
	fixcdata = re.compile(ur'(<!\[CDATA\[[^\]]*\])>')
	fixcdata2 = re.compile(ur'<!\[([^C][^\[]*\]\]>)')
	fixcdata3 = re.compile(ur'<!\[CDATA([^\[])')
	fixcdata4 = re.compile(ur'<([^>]*)>(<!\[CDATA\[[^\]]*)(\n\s*<[A-Z])')
	fixopentag = re.compile(ur'\n([^<>]*>)')
	for line in f:
		wordcount += 1
		word, fname = line.rstrip().split(u'\t', 1)
		mean = zipf.read(fname).decode('utf-16le')
		mean = mean.strip(u'\ufeff\0\r\n\t ')
		if not mean.endswith('</CK>'):
			mean += missingmatch(mean)
		mean = fixcdata4.sub(r'<\g<1>>\g<2>]]></\g<1>>\g<3>', mean)
		try:
			dom = parseString(mean.encode('utf-8')).childNodes[0]
		except ExpatError:
			mean = fixcdata.sub(r'\g<1>]>', mean)
			mean = fixcdata2.sub(r'<![CDATA[\g<1>]', mean)
			mean = fixcdata3.sub(r'<![CDATA[\g<1>', mean)
			mean = fixopentag.sub(r'\n<\g<1>', mean)
			try:
				missingmatch(mean)
			except:
				mean = fixmismatch(mean)
			try:
				dom = parseString(mean.encode('utf-8')
						).childNodes[0]
				ignore = True
			except ExpatError:
				ignore = False
			if not ignore:
				print >> sys.stderr, 'Error parsing', \
						mean.encode('gbk', 'replace')
				raise
		mean = ck2article(dom)
		try:
			assert mean.startswith(u'<k>%s</k>' % (word,))
		except:
			print >> sys.stderr, 'Warning: Different key phrase'
			print >> sys.stderr, u'<k>%s</k>' % (word,)
			print >> sys.stderr, mean[:mean.find(u'\n')]
		utf8writeln(u'<ar>%s</ar>' % (mean,))
	assert itemcount == wordcount

utf8writeln('</xdxf>')
zipf.close()
f.close()

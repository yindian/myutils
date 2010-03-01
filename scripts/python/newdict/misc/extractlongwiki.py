#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, htmlentitydefs, string, re
from xml.dom.minidom import parseString
import pdb

replace_dic = {}                                        #保存需要转换的HTML命名字符，如&nbsp; &lt;等
for name, codepoint in htmlentitydefs.name2codepoint.items():
	try:
		char = unichr(codepoint)            #enc编码可显示该HTML对象时，才进行替换
		replace_dic['&%s;' % name.lower()] = char
	except:
		pass

def trim(s):
	U"处理XML文件标记"
	s = s.replace('&amp;', '&')   #把UTF8编码转换为enc编码，无法编码的用?代替
	for name, char in replace_dic.iteritems():          #替换HTML命名字符
		s = s.replace(name, char)
	ar = s.split('&')
	for i in xrange(1, len(ar)):
		assert ar[i][0] == '#'
		p = ar[i].index(';')
		ar[i] = unichr(int(ar[i][1:p], 0)) + ar[p+1:]
	return ''.join(ar)

def getData(page, title):
	U"获取相应字段数据"
	try:
		return page.getElementsByTagName(title)[0].childNodes[0].data
	except:
		pdb.set_trace()
		return u''

tonetransform = {
	u'a': u'āáǎà',
	u'o': u'ōóǒò',
	u'e': u'ēéěè',
	u'i': u'īíǐì',
	u'u': u'ūúǔù',
	u'ü': u'ǖǘǚǜ',
	u'ê': u'\0ế\0ề',
	u'm': u'\0\0\0',
	u'n': u'\0ńň',
}
tonedict = {}
for alpha in tonetransform.iterkeys():
	for i in xrange(4):
		if tonetransform[alpha][i]:
			tonedict[tonetransform[alpha][i]] = (alpha, i+1)
specialpinyin = {
		u'bǎikè'	: u'bai3ke4' ,
		u'jiālún'	: u'jia1lun2',
		u'shíwǎ'	: u'shi2wa3' ,
		u'qiānwǎ'	: u'qian1wa3',
		u'fēnwǎ'	: u'fen1wa3' ,
		u'máowǎ'	: u'mao2wa3' ,
		u'bǎiwǎ'	: u'bai3wa3' ,
		u'lǐwǎ'	: u'li3wa3'  ,
		u'líwǎ'	: u'li2wa3'  ,
		}
def pinyinuntone(str):
	result = []
	tone = 0
	for c in str.replace(u'ɑ', u'a').replace(u'ɡ', u'g'):
		if c == u'ü':
			c = u'v'
		elif ord(c) >= 0x80:
			if tone != 0:
				return specialpinyin[str]
			c, tone = tonedict[c]
			if c == u'ü':
				c = u'v'
		result.append(c)
	return u''.join(result) + (tone and `tone` or u'')

assert __name__ == '__main__'

if len(sys.argv) != 2:
	print "Usage: %s wikidump.xml" % (os.path.basename(sys.argv[0]),)
	print "Output tabfile is written to console"
	sys.exit(0)

f = open(sys.argv[1], 'r')
s = f.read(3276800)
#pdb.set_trace()
restrkorder = re.compile(ur'笔顺编号:\s*([0-9]+)')
reunicpoint = re.compile(ur'UniCode:.*U.([0-9A-F]+)')
pinyinnotes = re.compile(ur'<py>(.*?)</py>')
end = 0
strokedict = {}
pinyindict = {}
basicinfo = '== 基本信息 =='
while True:
	try:
		start = s.index('<page>', end)
		end = s.index('</page>',start + 6) + 7
		part = s[start:end]
		dom = parseString(part)
	except Exception, e:
		tmp = f.read(3276800)
		if tmp:
			s += tmp
		else:
			break
	else:
		word = trim(getData(dom, 'title'))
		text = trim(getData(dom, 'text'))
		sects = filter(None, map(string.strip, text.split('\n== ')))
		assert sects
		if sects[0].startswith(u'基本信息') or sects[0].startswith(u'== 基本信息'):
			strokeorder = restrkorder.findall(sects[0])
			try:
				assert strokeorder
			except:
				#pdb.set_trace()
				print >> sys.stderr, 'No stroke order for', `word`
				continue
			assert len(strokeorder) == 1
			strokeorder = strokeorder[0]
			unicodepoint = reunicpoint.findall(sects[0])
			assert unicodepoint
			assert int(unicodepoint[0], 16) == ord(word)
			if len(sects) > 1 and sects[1].startswith(u'基本解释'):
				mean = pinyinnotes.sub(u'', sects[1][sects[1].index(u'\n')+1:]).replace(u'\n\n', u'\n')
				basic = pinyinnotes.sub(u'', sects[0][sects[0].index(u'\n')+1:]).replace(u'\n\n', u'\n').splitlines()
				print '%s\t%s\\n%s\\n%s' % (word.encode('utf-8'), mean.lstrip().encode('utf-8').replace('\n', '\\n'), basicinfo, u''.join(basic[2:]).encode('utf-8').replace('\n', '\\n'))
				ar = set(pinyinnotes.findall(sects[0]))
				for a in list(ar):
					if a+u'1' in ar:
						ar.discard(a)
				ar = list(ar)
				br = []
				for onemean in mean.split(u'\n==='):
					if not onemean:
						continue
					lines = onemean.splitlines()
					if lines[0].find(u'字义') > 0 or lines[0].find(u'字義') > 0:
						line = lines[1]
						if line.startswith(u'（') or line.startswith(u'*') or line.startswith(u'('):
							line = lines[2]
						try:
							p = line.find(u' ')
							if p < 0 or 0 < line.find(u'　') < p:
								p = line.find(u'　')
							if p < 0:
								p = line.find(u'＆#160;')
							if p < 0:
								p = line.find(u'（')
							br.append(line[:p].replace('B', 'a').replace(u'<', u'ü'))
							assert not br[-1] or br[-1].isalpha() or br[-1] in (u'', u'g', u'ńg', u'ňg')
							if len(br[-1]) == 1:
								assert ord(br[-1]) < 0x3000 or br[-1] == u''
						except Exception, e:
							print >> sys.stderr, `e`, `word`, br
							del br[-1]
							continue
							pdb.set_trace()
							raise
				try:
					assert not ar or len(ar) == len(br)
				except:
					#pdb.set_trace()
					#print >> sys.stderr, word.encode('gbk', 'replace'), mean.encode('gbk', 'replace')
					#print >> sys.stderr, ar, br
					#raw_input()
					pass
				if len(br) > len(ar):
					pr = br
				else:
					pr = ar
				try:
					pr = map(pinyinuntone, pr)
				except:
					pdb.set_trace()
					raise
				if not strokedict.has_key(strokeorder):
					strokedict[strokeorder] = []
				strokedict[strokeorder].append(word)
				for pinyin in pr:
					if not pinyindict.has_key(pinyin):
						pinyindict[pinyin] = []
					pinyindict[pinyin].append(word)
			elif len(sects) > 2:
				assert not sects[2].startswith(u'基本解释')
		else:
			raise Exception('Not a character')
		#print word.encode('gbk', 'replace'), strokeorder, unicodepoint
		if len(s) > 30000000:
			s = s[end:]
			end = 0
f.close()
for pinyin in sorted(pinyindict.iterkeys()):
	pinyindict[pinyin].sort()
	print '%s\t%s' % (pinyin.encode('ascii'), u'  '.join(pinyindict[pinyin]).encode('utf-8'))
for strokeorder in sorted(strokedict.iterkeys()):
	strokedict[strokeorder].sort()
	print '%s\t%s' % (strokeorder.encode('ascii'), u'  '.join(strokedict[strokeorder]).encode('utf-8'))

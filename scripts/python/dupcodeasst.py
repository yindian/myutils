#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path
import pprint, pdb

def cjkclass(c):
	if not c:
		return 0
	if type(c) != type(u''):
		c = c.decode('utf-8')
	code = ord(c[0])
	if 0xD800 <= code < 0xDC00:
		if len(c) < 2 or not 0xDC00 <= ord(c[1]) < 0xE000:
			return 0
		code = 0x10000+ (((code - 0xD800) << 10) | (ord(c[1]) - 0xDC00))
	if 0x4E00 <= code <= 0x9FFF: # URO (up to 0x9FA5) or CJK Basic
		return 1
	elif 0xF900 <= code <= 0xFAFF: # CJK Compat
		return 2
	elif 0x3400 <= code <= 0x4DBF: # CJK Ext-A
		return 3
	elif 0x20000 <= code <= 0x2A6DF: # CJK Ext-B
		return 4
	elif 0x2F800 <= code <= 0x2FA1F: # CJK Compat Supplement
		return 5
	elif 0x2A700 <= code <= 0x2B73F: # CJK Ext-C
		return 6
	elif 0x2B740 <= code <= 0x2B81F: # CJK Ext-D
		return 7
	else:
		return 0

iscjk = lambda c: cjkclass(c) > 0
notids = lambda c: not 0x2FF0 <= ord(c) <= 0x2FFF

def char2utf8(code):
	if code < 0x10000:
		return unichr(code).encode('utf-8')
	else:
		assert code < 0x200000
		return ''.join(map(chr, [
			0xf0 | (code >> 18),
			0x80 | ((code >> 12) & 0x3f),
			0x80 | ((code >> 6) & 0x3f),
			0x80 | (code & 0x3f)]))

def loadIDS(chisepath):
	ids = {}
	fnlist = '''\
IDS-CDP.txt
IDS-CNS-1.txt
IDS-CNS-2.txt
IDS-Daikanwa-02.txt
IDS-UCS-Basic.txt
IDS-UCS-Compat-Supplement.txt
IDS-UCS-Compat.txt
IDS-UCS-Ext-A.txt
IDS-UCS-Ext-B-1.txt
IDS-UCS-Ext-B-2.txt
IDS-UCS-Ext-B-3.txt
IDS-UCS-Ext-B-4.txt
IDS-UCS-Ext-B-5.txt
IDS-UCS-Ext-B-6.txt\
'''.splitlines()
	for fname in fnlist:
		f = open(os.path.join(chisepath, fname), 'r')
		lineno = 0
		try:
			for line in f:
				lineno += 1
				if line.startswith(';'):
					continue
				line = line.strip(' \r\n')
				if not line:
					continue
				ar = line.split('\t')
				assert len(ar) == 3 or (len(ar) == 4 and
						ar[3] == '?')
				if ar[0][0] == 'U' and ar[0][1] in '+-':
					code = int(ar[0][2:], 16)
					assert char2utf8(code) == ar[1]
				ids[ar[1]] = ar[2].decode('utf-8')
		except:
			print >> sys.stderr, 'Error on %s:%d' % (fname, lineno)
			raise
		f.close()
	return ids

specialids = { # for wubi
		'&CDP-897D;':	u'⿻三丿', # 寿 上部
		'&CDP-8BE9;':	u'⿻三人', # 春 上部
		'&CDP-8BFA;':	u'⿻䒑大', #拳 上部
		'&CDP-89BE;':	u'⿻白丿', # 卑 上部
		'&CDP-8C62;':	u'⿻巾𠓜', # 兩 下部
		'&CDP-88F1;':	u'⿱𠂇丨', # 在 外部
		'&M-08757;':	u'⿰𦣝巳', # 煕 上部
		'&CDP-8D5B;':	u'⿻土从', # 嗇 上部
		'&CDP-8C7A;':	u'⿹コ⿰丨二', #叚 左部
		'&CDP-8BB7;':	u'⿱⿻二刂一', #冓 上部
		'&GT-03877;':	u'⿱一厶', # 至 上部
		'&CDP-88D6;':	u'⿻⿱八⿵冂㸚丨', # 爾 下部
		'&CDP-8BD3;':	u'⿱廿⿻⿱口二大', # 嘆 右下部
		'&C1-4441;':	u'⿱亠𠃊', # 亡
		'&CDP-85A8;':	u'⿻千𠈌', # 𪍰 右部
		'&GT-K05506;':	u'⿱左月', # 隋 右部
		'&CDP-89C5;':	u'⿻⿰⿻口一口丨', # 婁 上部
		'&CDP-8B6A;':	u'⿱厶月', # 能 左部
		'&GT-14783;':	u'⿸戶方', # 房 异体
		'&CDP-89E5;':	u'⿻⿱一彐丨', # 妻 上部
		'&M-00573;':	u'使', # 异体
		'&CDP-8C4F;':	u'&CDP-8C4F;', # 祭 上部
		'&CDP-89F4;':	u'⿻口人', # 検 右下部
		'&GT-01002;':	u'倉', # 异体
		'&CDP-8DDD;':	u'⿱⿱一口丨', # 囊 最上部
		'&CDP-88EB;':	u'⿰⿱丿干⿱丿干', # 倂 右部
		'&CDP-8DCB;':	u'⿻⿱彐月丨', # 庸 内部
		'&GT-39640;':	u'⿻羊八', # 業 下部
		'&CDP-8C44;':	u'⿻彐丨', # 唐 内上部
		'&C1-5249;':	u'甚', # 异体
		'&C4-2F31;':	u'𦐇', # 塌 右部 异体
		'&CDP-89DD;':	u'㦮', # 銭 右部
		'&C3-2548;':	u'囱', # 异体
		'&CDP-876E;':	u'⿻⿱一卄十', # 華 下部除底横
		'&CDP-85D5;':	u'⿻人丷', # 𣋴 中部
		'&CDP-87FB;':	u'⿻⿱吅冂⿱⿰丨一丶', # 𠎘 下部
		'&CDP-8AF0;':	u'⿻丿七', # 扥 右部
		'坐':		u'⿻从土',
		'韱':		u'⿹⿱从戈韭',
		'谷':		u'⿳八人口',
		'豆':		u'⿳一口䒑',
		#'非':		u'⿲三刂三',
		'卝':		u'⿲一刂一',
		'戉':		u'⿻⿻匚乚⿱丶丿',
		'辰':		u'⿸厂⿱二&CDP-8C66;',
		'夾':		u'⿻大从',
		'幾':		u'⿱𢆶戍',
		'吏':		u'⿻⿱一口乂',
		'垂':		u'⿻⿳丿一卄士',
		'重':		u'⿻⿳丿一日士',
		'埀':		u'⿻⿳丿一北士',
		'乖':		u'⿻千北',
		'乘':		u'⿻禾北',
		'甫':		u'⿺⿻⿱一月丨丶',
		'两':		u'⿱一⿻冂从',
		'不':		u'⿱一小',
		'互':		u'⿱一彑',
		'歹':		u'⿱一夕',
		'頁':		u'⿱丆貝',
		'亍':		u'⿱二丨',
		'阜':		u'⿱𠂤十',
		'𡗜':		u'⿻大丷',
		'𦍌':		u'⿱丷王',
		'𠂹':		u'⿻亻𠈌',
		'𨸏':		u'⿱𠂤コ',
		}
def _getids(ids, newids, word):
	if newids.has_key(word):
		return newids[word]
	if not ids.has_key(word) and not specialids.has_key(word):
		return None
	result = []
	newids[word] = None
	i = 0
	olddecomp = specialids.get(word, None) or ids[word]
	while i < len(olddecomp):
		j = i+1
		if 0xD800 <= ord(olddecomp[i]) < 0xDC00:
			j += 1
		elif olddecomp[i] == '&':
			j = olddecomp.index(';', i) + 1
		part = olddecomp[i:j].encode('utf-8')
		partids = _getids(ids, newids, part)
		if partids is None:
			partids = olddecomp[i:j]
		result.append(partids)
		i = j
	newids[word] = ''.join(result)
	return newids[word]

firstclasscomp = u'''\
其
甚
匚大人
匚爿
臣
臣𠂉
臣𠂉一
𦣝
艸
矛
敄
叕
叒
厽
&GT-K00064;&GT-K00064;&GT-K00064;
丆
而
面
镸山&C1-454B;
垚
封
𠦄
⺿士
⺿土
⺿一
⺿五
壴
喜
鼓
𣪊
士冖一
士冖王
士冖一几又
十冖一几又
士冖几又王
壹
老
一口丨
一口丨冖
一口丨冖木
束
齒
目人人
目八人
止谷
⻊艹
⻊廿
口虍
⻊厂
⻊三
⻊大
⻊𠂇
⻊匚
黑
田田田田
田田田
田田囗
風
爿
韋
饣丿
&CDP-8976;丿
钅丿一
金丿一
⺨一
⺨王
金夂一
金生
卵
鬼
&GT-61541;
⻤
來
來&GT-K00207;
木亻人
毛
⺮士⺄
⺮土乛
𠂉十&CDP-88B6;
片
&C1-455A;
&GT-00120;
&CDP-8DD9;
身
夂貝丆
彳山戊
彳韋
彳二丨韋
&J83-3152;
衛
䘙
丷
䒑
齊
&CDP-8DEB;&CDP-8BF5;
鼠
人一口
&GT-00458;一口
⺅一口
癶一口
&CDP-8C4F;一口
㑒
&GT-K03992;
龠
𠂤
&CDP-8CBB;
烏
鳥
谷
飠
⻞
&GT-00458;丶&CDP-89CE;
&GT-00458;一&CDP-8B7C;
&GT-00458;丶艮
⺅亠刀丫&CDP-89CA;丿
⺅&CDP-8DEB;
⺅广彐
幾
高
鹿
&CDP-8D56;
&C1-5E26;
广&CDP-88B4;
亡中一
亡口月几丶
&M-00287;口&CDP-8A73;&CDP-88EC;
亡口⺼⺄
亡口⺼几丶
&CB12237;
麻
'''.splitlines()

def expandIDS(ids):
	newids = {}
	for atom in firstclasscomp:
		atom = atom.encode('utf-8')
		while atom:
			l = 0
			c = ord(atom[0])
			while c & 0x80:
				c <<= 1
				l += 1
			if l == 0:
				l = 1
				atom = atom[l:]
				continue
			newids[atom[:l]] = atom[:l].decode('utf-8')
			atom = atom[l:]
	for word in ids.iterkeys():
		_getids(ids, newids, word)
	return newids

altcomp = {
		'&GT-36329;':	'罒',
		'&J83-3227;':	'翁',
		'&B-B3BF;':	'鹵',
		'&GT-00458;':	'人',
		'&CDP-8AF2;':	'臦 左部',
		'&CDP-88B6;':	'丩',
		'&I-C4-2535;':	'𠈌',
		'&CDP-8B5B;':	'⺈',
		'&GT-01891;':	'兮',
		'&GT-13174;':	'念',
		'&CDP-86E2;':	'H',
		'&CDP-8B56;':	'𠀉',
		'&GT-57204;':	'靡',
		'&GT-K00064;':	'又',
		'&CDP-8958;':	'月',
		'&CDP-88F0;':	'炙 上部',
		'&C1-4443;':	'刃',
		'&GT-K00199;':	'土',
		'&CDP-89BE;':	'白 加撇',
		'&GT-K05014;':	'堂 上部',
		'&C1-5038;':	'咨',
		'&C2-286B;':	'豖',
		'&M-02691;':	'區',
		'&J83-6C35;':	'豕',
		'&CDP-8B6C;':	'刀',
		'&GT-03877;':	'至 上部',
		'&GT-00033;':	'丑',
		'&GT-14544;':	'戈',
		'&C1-454B;':	'曰',
		'&CDP-8D61;':	'曹 上部',
		'&M-02690;':	'匿',
		'&GT-00379;':	'亢',
		'&GT-37565;':	'耳',
		'&I-CDP-8D64;':	'夋',
		'&CDP-8C62;':	'巾 加从',
		'&C5-4A7B;':	'𨾴',
		'&GT-K01023;':	'令',
		'&GT-00376;':	'亠',
		'&GT-29752;':	'真',
		'&GT-04222;':	'吟',
		'&CDP-8BD0;':	'惠 上部',
		'&GT-00132;':	'丸',
		'&CDP-8BD5;':	'覀',
		'&CDP-8C69;':	'留 上部',
		'&B-AAF7;':	'金',
		'&CDP-8DEE;':	'曺 上部',
		'&GT-00467;':	'今',
		'&CDP-8C78;':	'コ',
		'&CDP-8CE4;':	'段 左部',
		'&CDP-8976;':	'饣',
		'&CDP-8BC5;':	'北 左部',
		'&GT-61541;':	'鬼',
		'&C1-4464;':	'丰 撇起',
		'&CDP-8DD8;':	'⺈',
		'&CDP-8BA5;':	'具 上部',
		'&GT-K00059;':	'八',
		'&GT-K00207;':	'夕',
		'&CDP-8A78;':	'日 冃',
		'&C1-484D;':	'米',
		'&C1-4C78;':	'宗',
		'&CDP-8AC2;':	'𦒫 左部',
		'&GT-00120;':	'𣶒',
		'&CDP-8DD9;':	'𣶒',
		'&C1-455A;':	'片',
		'&CDP-89A7;':	'卩',
		'&GT-21312;':	'段',
		'&C4-2234;':	'关',
		'&GT-11620;':	'广',
		'&M-00782;':	'倠',
		'&GT-01783;':	'免',
		'&M-29237;':	'月',
		'&CDP-8A73;':	'月',
		'&GT-00458;':	'人',
		'&GT-K03992;':	'㑒',
		'&CDP-8CBB;':	'鳥 外部',
		'&CDP-8974;':	'丁',
		'&GT-52197;':	'過',
		'&GT-11685;':	'底',
		'&GT-11011;':	'差',
		'&CDP-8D41;':	'𠂎',
		'&M-24623;':	'示',
		'&M-30640;':	'䒑',
		'&CDP-89B6;':	'畱 上部',
		'&CDP-8B7C;':	'即 左部',
		'&CDP-89EB;':	'以 左部',
		'&GT-00644;':	'似',
		'&CDP-8BBF;':	'与 外部',
		'&C1-5E26;':	'鹿',
		'&I-C4-2249;':	'𠫤',
		'&GT-59026;':	'食',
		'&CDP-8BA9;':	'牜',
		'&GT-03427;':	'匚',
		}
def addcompcode(word2code):
	word2code['H'] = 'hgh'
	word2code['&CDP-8C66;'] = 'e'
	word2code['&CDP-8B67;'] = 'e'
	word2code['コ'] = 'nng'

def getassistcodes(wordlist, word2code, ids):
	result = []
	word = refword = None
	for i in xrange(len(wordlist)):
		word = wordlist[i]
		if word not in ids:
			#print >> sys.stderr, 'Missing', word
			result.append((word, '?', 'Missing'))
			continue
		#refword = wordlist[i == 0 and 1 or 0]
		#if refword not in ids:
		#	print >> sys.stderr, 'Missing', refword
		#	break
		decomp = ''.join(filter(notids, ids[word]))
		#refdecomp = ''.join(filter(notids, ids[refword]))
		#for p in xrange(min(len(decomp), len(refdecomp))):
		#	if decomp[p] != refdecomp[p]:
		#		break
		#try:
		#	assert decomp[p] != refdecomp[p]
		#except:
		#	print >> sys.stderr, word, refword, p,
		#	print >> sys.stderr, decomp.encode('utf-8'),
		#	print >> sys.stderr, refdecomp.encode('utf-8')
		#	pass
		#while p > 0 and not (iscjk(decomp[p:p+2]) or decomp[p] == '&'):
		#	p -= 1
		#while p < len(decomp)-1 and not (iscjk(decomp[p:p+2]) or
		#		decomp[p] == '&'):
		#	p += 1
		p = -1
		for s in firstclasscomp:
			if s and decomp.startswith(s) and len(s) > p:
				p = len(s)
		if p < 0 or p == len(decomp):
			part = 'Unknown'
		elif 0xD800 <= ord(decomp[p]) < 0xDC00:
			part = decomp[p:p+2]
		elif decomp[p] == '&':
			part = decomp[p:decomp.index(';', p)+1]
		else:
			part = decomp[p]
		part = part.encode('utf-8')
		part = altcomp.get(part, part)
		result.append((word,word2code.get(part.split()[0],'?')[0],part))
	return result

assert __name__ == '__main__'

if len(sys.argv) != 4:
	print 'Usage: %s mb.txt chise_path out_mb_w_asst.txt' % (
			os.path.basename(sys.argv[0]),)
	print 'mb input format: each line is space separated code & word'
	print 'All input/output files are UTF-8 encoded.'
	sys.exit(0)

print >> sys.stderr, 'Loading MB...'
code2word = {}
word2code = {}
f = open(sys.argv[1], 'r')
for line in f:
	code, word = line.strip().split()
	if not code2word.has_key(code):
		code2word[code] = []
	if word not in code2word[code]:
		code2word[code].append(word)
	if 1: #not word2code.has_key(word) or len(code) > len(word2code[word]):
		word2code[word] = code
f.close()

duplist = []
for code in sorted(code2word.iterkeys()):
	if len(code2word[code]) > 10:
		#print '%s\t%s' % (code, ' '.join(code2word[code]))
		duplist.append((code, filter(iscjk, code2word[code])))

print >> sys.stderr, 'Loading IDS...'
ids = loadIDS(sys.argv[2])
ids = expandIDS(ids)
for c in sorted(ids.iterkeys()):
	print '%s\t%s' % (c, ids[c].encode('utf-8'))
addcompcode(word2code)

print >> sys.stderr, 'Generating assist codes...'
f = open(sys.argv[3], 'w')
for code, wordlist in duplist:
	#if code == 'fpgc':
	#	pdb.set_trace()
	if len(code) < 4 or len(wordlist) < 2:
		continue
	assistcodes = getassistcodes(wordlist, word2code, ids)
	for word, asstcode, part in assistcodes:
		print >> f, '%s%s %s # %s' % (code, asstcode, word, part)
f.close()

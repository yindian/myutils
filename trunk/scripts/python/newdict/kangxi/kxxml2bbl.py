#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob, pprint
import libxml2dom
from libxml2dom import Node

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

assert __name__ == '__main__'

XML_CATEGORIES = "Tbl_Catalog.xml";
XML_RADICALS = "Tbl_BS.xml";
XML_INFOS = "Tbl_KX.xml";
XML_READINGS = "Tbl_PY.xml";
TEXT_INFOS = "FDetailCmps.txt";

categoryMap = {};
radicalMap = {};
characterMap = {};
NUM_RADICALS = 0

document = libxml2dom.parseString(open(XML_CATEGORIES, 'r').read());

for child in document.firstChild.childNodes:
	if (child.nodeType != Node.ELEMENT_NODE):
		continue;
	# <Tbl_Catalog>
	id = 0;
	sName = None;
	radicals = [];
	for child2 in child.childNodes:
		if (child2.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName = child2.tagName;
		if (sTagName in ("CatalogID")):
			id = int((child2).textContent) - 1;
		elif (sTagName in ("CatalogVal")):
			sName = (child2).textContent;
		elif (sTagName in ("BS")):
			# 含まれる部首
			s = (child2).textContent;
			radicals = [0] * (len(s) / 3);
			for i in range(len(radicals)):
				radicals[i] = int(s[i * 3: i * 3 + 3]) - 1;
	infoMap = {}
	infoMap.__setitem__("name", sName);
	infoMap.__setitem__("radicals", radicals);
	categoryMap.__setitem__(int(id), infoMap);

#pprint.pprint(categoryMap)
#sys.exit(0)

document = libxml2dom.parseString(open(XML_RADICALS, 'r').read());
for child in document.firstChild.childNodes:
	if (child.nodeType != Node.ELEMENT_NODE):
		continue;
	# <Tbl_BS>
	id = 0;
	sCharacter = "";
	strokes = 0;
	for child2 in child.childNodes:
		if (child2.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName = (child2).tagName;
		if (sTagName in ("PartID")):
			id = int(child2.textContent) - 1;
		elif (sTagName in ("WordPart")):
			sCharacter = child2.textContent.strip();
		elif (sTagName in ("PartCount")):
			strokes = int(child2.textContent)	;
		elif (sTagName in ("BWCount")):
			# 部首外画数群
			pass
		elif (sTagName in ("BWNotBB")):
			# 普通部首外画数群
			pass
		elif (sTagName in ("BWBK")):
			# 備考部首外画数群
			pass
		elif (sTagName in ("BWBY")):
			# 補遺部首外画数群
			pass
	infoMap = {}
	infoMap.__setitem__("character", sCharacter);
	infoMap.__setitem__("strokes", int(strokes));
	radicalMap.__setitem__(int(id), infoMap);
document = libxml2dom.parseString(open(XML_INFOS, 'r').read());
codePoints = [0] * 47043;
for child in document.firstChild.childNodes:
	if (child.nodeType != Node.ELEMENT_NODE):
		continue;
	# <Tbl_KX>
	id = 0;
	categoryId = 0;
	sCharacter = None;
	codePoint = 0;
	radicalId = 0;
	infoMap = {}
	for child2 in child.childNodes:
		if (child2.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName = (child2).tagName;
		if (sTagName in ("WordID")):
			id = int(child2.textContent) - 1;
#					infoMap.__setitem__("id", int(id));
		elif (sTagName in ("CatalogID")):
			categoryId = int(child2.textContent) - 1;
			infoMap.__setitem__("category", int(categoryId));
		elif (sTagName in ("WordName")):
			sCharacter = child2.textContent;
		elif (sTagName in ("UCode")):
			s = child2.textContent;
			if len(s) == 4:
				codePoint = int(s, 16);
			elif len(s) == 8:
				code0 = int(s[0: 4], 16);
				code1 = int(s[4: 8], 16);
				codePoint = ((code0 - 0xD800) << 10) + (
						(code1 - 0xDC00)) + 0x10000
#					codePoints[index] = codePoint;
		elif (sTagName in ("BBFlg")):
			# categoryType
			s = child2.textContent;
			# W ...
			# B ... 補遺
			# K ... 備考
			infoMap.__setitem__("categoryType", s);
		elif (sTagName in ("Word1")):
			pass
		elif (sTagName in ("Word2")):
			pass
		elif (sTagName in ("BW1")):
			pass
		elif (sTagName in ("BW2")):
			pass
		elif (sTagName in ("BWCount")):
			# 部首外画数
			infoMap.__setitem__("strokes", int(child2.textContent));
		elif (sTagName in ("PartID")):
			radicalId = int(child2.textContent) - 1;
			if radicalId >= NUM_RADICALS:
				NUM_RADICALS = radicalId + 1
			infoMap.__setitem__("radical", int(radicalId));
		elif (sTagName in ("DetailCmp")):
			pass
		elif (sTagName in ("FDetailCmp")):
			pass
	characterMap.__setitem__(int(codePoint), infoMap);
	codePoints[id] = codePoint;
radicalsMaps = [[{}] * NUM_RADICALS, [{}] * NUM_RADICALS, [{}] * NUM_RADICALS]
i = 0
for sLine in open(TEXT_INFOS, 'r'):
	sLine = unicode(sLine, 'utf-8')
	codePoint = codePoints[i];
	infoMap = characterMap.get(int(codePoint));
	infoMap.__setitem__("kangxi", sLine);
	characterMap.__setitem__(int(codePoint), infoMap);
	
	radical = infoMap.get("radical");
	sCategoryType = infoMap.get("categoryType");
	categoryType = 0;
	if (sCategoryType in ("B")):
		categoryType = 1;
	elif (sCategoryType in ("K")):
		categoryType = 2;
	strokes = infoMap.get("strokes");
	
	try:
		iCodePointListMap = radicalsMaps[categoryType][radical];
	except IndexError:
		print 'categoryType =', categoryType, 'radical =', radical
		print 'NUM_RADICALS =', NUM_RADICALS
		raise
	iCodePointList = iCodePointListMap.get(int(strokes));
	if (iCodePointList == None):
		iCodePointList = []
		iCodePointListMap.__setitem__(int(strokes), iCodePointList);
	iCodePointList.append(int(codePoint));
	
	i += 1
assert i == 47043
characterMap.__setitem__(int(0), radicalsMaps);

for i in range(47043):
	#print i, hex(codePoints[i]), characterMap[codePoints[i]]
	infoMap = characterMap.get(int(codePoints[i]));
	sys.stdout.writelines([
		char2utf8(codePoints[i]),
		'\t',
		])
	if infoMap["categoryType"] == "B":
		sys.stdout.write(u'\u3010\u88dc\u907a\u3011'.encode('utf-8'))
	elif infoMap["categoryType"] == "K":
		sys.stdout.write(u'\u3010\u5099\u8003\u3011'.encode('utf-8'))
	sys.stdout.writelines([
		(u'\u3010%s\u3011' % (categoryMap[infoMap["category"]]["name"])
			).encode('utf-8'),
		(u'\u3010%s\u5b57\u90e8\u3011' % (radicalMap[infoMap["radical"]
			]["character"])).encode('utf-8'),
		'\\n',
		char2utf8(codePoints[i]),
		'\\n',
		infoMap["kangxi"].replace(u'\n', u'\\n').encode('utf-8'),
		'\n',
		])

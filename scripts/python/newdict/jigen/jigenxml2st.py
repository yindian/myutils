#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, re, glob, pprint
import libxml2dom
from libxml2dom import Node

try:
	fnenc = 'utf-8'
	from ctypes import windll
	from ctypes.wintypes import DWORD
	STD_OUTPUT_HANDLE = DWORD(-11)
	STD_ERROR_HANDLE = DWORD(-12)
	GetStdHandle = windll.kernel32.GetStdHandle
	WriteConsoleW = windll.kernel32.WriteConsoleW

	def writeunicode(ustr, file=sys.stdout, newline=True):
		if file in (sys.stdout, sys.stderr) and file.isatty():
			which = file==sys.stdout and STD_OUTPUT_HANDLE or STD_ERROR_HANDLE;
			handle = GetStdHandle(which)
			if not isinstance(ustr, unicode):
				ustr = unicode(ustr)
			WriteConsoleW(handle, ustr, len(ustr), None, 0)
			if newline:
				print >> file
		else:
			if newline:
				print >> file, ustr.encode(fnenc, 'replace')
			else:
				file.write(ustr.encode(fnenc, 'replace'))
except:
	def writeunicode(ustr, file=sys.stdout, newline=True):
		if newline:
			print >> file, ustr.encode(fnenc, 'replace')
		else:
			file.write(ustr.encode(fnenc, 'replace'))

numhandict = {
		1:  u'一',
		2:  u'二',
		3:  u'三',
		4:  u'四',
		5:  u'五',
		6:  u'六',
		7:  u'七',
		8:  u'八',
		9:  u'九',
		10: u'十',
	}

def num2Han(num):
	assert num > 0 and num < 100
	if num <= 10:
		return numhandict[num]
	elif num < 20:
		return numhandict[10] + numhandict[num-10]
	elif num % 10 == 0:
		return numhandict[num / 10] + numhandict[10]
	else:
		return numhandict[num / 10] + numhandict[10] + numhandict[num % 10]

kaeriten = {
		u'レ':  u"\u3191",
		u'一':  u"\u3192",
		u'二':  u"\u3193",
		u'三':  u"\u3194",
		u'四':  u"\u3195",
		u'上':  u"\u3196",
		u'中':  u"\u3197",
		u'下':  u"\u3198",
		u'甲':  u"\u3199",
		u'乙':  u"\u319A",
		u'丙':  u"\u319B",
		u'丁':  u"\u319C",
	}

def getWordContent(child2):
	assert child2.tagName == u'熟語'
	infoList = []
	sWord = None
	for child3 in child2.childNodes:
		if (child3.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName3 = (child3).tagName;
		if (sTagName3 == (u"見出語")):
			sWord = child3.textContent.strip();
			try:
				assert len(sWord) >= 2
			except:
				print >> sys.stderr, 'Word = ',
				writeunicode(sWord, sys.stderr)
				raise
			sValue = []
			for child4 in child3.childNodes:
				if (child4.nodeType == Node.ELEMENT_NODE):
					assert child4.tagName == u"返点"
					sType = (child4).getAttribute(u"type");
					for j in range(len(sType)):
						sValue += [kaeriten[sType[j]]];
				elif child4.nodeType == Node.TEXT_NODE:
					sValue += [child4.textContent.strip()];
			infoList.append(u"【熟語】" + u''.join(sValue));
		elif (sTagName3 == (u"音")):
			infoList.append(u"【音】" + child3.textContent.strip());
		elif (sTagName3 == (u"解")):
			sValue = [];
			for child5 in child3.childNodes:
				if (child5.nodeType != Node.ELEMENT_NODE):
					continue;
				sTagName5 = (child5).tagName;
				if (sTagName5 == (u"號")):
					sValue += [child5.textContent];
				elif (sTagName5 == (u"義")):
					sValue2 = [];
					# <音>
					# <標識>
					# <返点 type=u"[レ一二三上中下]|一レ|上レ">
					for child6 in child5.childNodes:
						if child6.nodeType == Node.ELEMENT_NODE:
							sTagName6 = (child6).tagName;
							if (sTagName6 == (u"音")):
								sValue2 += [u"(" , child6.textContent , u")"];
							elif (sTagName6 == (u"標識")):
								sValue2 += [u"[" , child6.textContent , u"]"];
							elif (sTagName6 == (u"返点")):
								sType = (child6).getAttribute(u"type");
								for j in range(len(sType)):
									sValue2 += [kaeriten[sType[j]]];
							else:
								raise
						elif child6.nodeType == Node.TEXT_NODE:
							sValue2 += [child6.textContent.strip()];
						else:
							raise
					sValue += [u''.join(sValue2) , u"\n"];
			infoList.append(u"【解】\n" + u''.join(sValue));
		else:
			print >> sys.stderr, 'Tagname3 = ',
			writeunicode(sTagName3, sys.stderr)
			raise
	assert sWord is not None
	return (sWord, infoList)
	

assert __name__ == '__main__'

resultList = []
characterMap = {};
radicalMap = {}
NUM_RADICALS = 214

charCount = 0
wordCount = 0

for i in range(NUM_RADICALS):
	document = libxml2dom.parseString(open('%03d.xml' % (i+1), 'r').read());
	sRadical = None;
	radicalList = []
	lastStrokes = -1
	print >> sys.stderr, 'Processing %03d.xml' % (i+1)
	for child in document.getElementsByTagName(u'部首')[0].childNodes:
		if (child.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName = (child).tagName;
		if (sTagName == (u"部首字")):
			try:
				assert len(child.textContent.strip()) == 2
			except:
				print >> sys.stderr, 'Len not 2: ',
				writeunicode(child.textContent, sys.stderr)
			sRadical = u"" + child.textContent[0];
			radicalList.append(u"【部首】" + sRadical + u"  番号%d" % (i+1));
		elif (sTagName == (u"筆畫")):
			strokes = -1;
			for child2 in child.childNodes:
				if (child2.nodeType != Node.ELEMENT_NODE):
					continue;
				sTagName2 = (child2).tagName;
				if (sTagName2 == (u"畫數")):
					strokes = int(child2.textContent);
					try:
						assert strokes > lastStrokes
					except:
						print >> sys.stderr, 'Strokes = %d, last strokes = %d' % (strokes, lastStrokes)
						raise
					lastStrokes = strokes
					if strokes > 0:
						radicalList.append(u"\n\n筆畫" + num2Han(strokes) + u"\n");
					else:
						radicalList.append(u"\n\n");
				elif (sTagName2 == (u"漢字")):
					sCharacter = None;
					codePoint = 0;
					wordList = [];
					
					infoList = [];
					infoList.append(u"【部首】" + sRadical);
					infoList.append(u"【畫數】 %d" % strokes);

					for child3 in child2.childNodes:
						if (child3.nodeType != Node.ELEMENT_NODE):
							continue;
						sTagName3 = (child3).tagName;
						if (sTagName3 == (u"見出字")):
							sCharacter = child3.textContent;
							if (not sCharacter == (u"？")):
								try:
									codePoint = ord(sCharacter);
								except:
									try:
										assert len(sCharacter) == 2
										assert 0xD800 <= ord(sCharacter[0]) <= 0xDBFF and 0xDC00 <= ord(sCharacter[1]) <= 0xDFFF
										codePoint = ((ord(sCharacter[0]) - 0xD800) << 10) + (
												(ord(sCharacter[1]) - 0xDC00)) + 0x10000
									except:
										if not sCharacter.startswith(u'{'):
											print >> sys.stderr, 'sCharacter = ',
											writeunicode(sCharacter, sys.stderr)
											raise
							infoList.append(u"【親字】" + sCharacter);
							radicalList.append(u" " + sCharacter);
						elif (sTagName3 == (u"字解")):
							for child4 in child3.childNodes:
								if (child4.nodeType != Node.ELEMENT_NODE):
									continue;
								sTagName4 = (child4).tagName;
								if (sTagName4 == (u"音韻")):
									sValue = [];
									for child5 in child4.childNodes:
										if (child5.nodeType != Node.ELEMENT_NODE):
											continue;
										sTagName5 = (child5).tagName;
										if (sTagName5 == (u"號")):
											sValue += [child5.textContent];
										elif (sTagName5 == (u"音")):
											sValue += [u"「" , child5.textContent , u"」"];
										elif (sTagName5 == (u"韻")):
											sValue += [u"[" , child5.textContent , u"]"];
										else:
											raise
									infoList.append(u"【音韻】" + u''.join(sValue));
								elif (sTagName4 == (u"字解註")):
									# <標識>
									sValue = []
									for child5 in child4.childNodes:
										if (child5.nodeType) == Node.ELEMENT_NODE:
											sTagName5 = (child5).tagName;
											if (sTagName5 == (u"標識")):
												sValue += [u"[" , child5.textContent , u"]"];
										elif child5.nodeType == Node.TEXT_NODE:
											sValue += [child5.textContent.strip()];
										else:
											raise
									infoList.append(u"【字解註】" + u''.join(sValue));
								elif (sTagName4 == (u"解")):
									sValue = [];
									for child5 in child4.childNodes:
										if (child5.nodeType != Node.ELEMENT_NODE):
											continue;
										sTagName5 = (child5).tagName;
										if (sTagName5 == (u"號")):
											sValue += [child5.textContent];
										elif (sTagName5 == (u"義")):
											sValue2 = [];
											# <音>
											# <標識>
											# <返点 type=u"[レ一二三上中下]|一レ|上レ">
											for child6 in child5.childNodes:
												if child6.nodeType == Node.ELEMENT_NODE:
													sTagName6 = (child6).tagName;
													if (sTagName6 == (u"音")):
														sValue2 += [u"(" , child6.textContent , u")"];
													elif (sTagName6 == (u"標識")):
														sValue2 += [u"[" , child6.textContent , u"]"];
													elif (sTagName6 == (u"返点")):
														sType = (child6).getAttribute(u"type");
														for j in range(len(sType)):
															sValue2 += [kaeriten[sType[j]]];
													else:
														raise
												elif child6.nodeType == Node.TEXT_NODE:
													sValue2 += [child6.textContent.strip()];
												else:
													raise
											sValue += [u''.join(sValue2) , u"\n"];
									infoList.append(u"【解】\n" + u''.join(sValue));
								elif (sTagName4 == (u"解字")):
									# <標識>
									sValue = [];
									for child5 in child4.childNodes:
										if child5.nodeType == Node.ELEMENT_NODE:
											sTagName5 = child5.tagName
											if (sTagName5 == (u"標識")):
												sValue += [u"[" , child5.textContent , u"]"];
										elif child5.nodeType == Node.TEXT_NODE:
											sValue += [child5.textContent.strip()];
										else:
											raise
									infoList.append(u"【解字】" + u''.join(sValue));
								elif (sTagName4 == (u"同訓")):
									# <標識>
									# <訓>
									# <同訓字>
									# <同訓解>
									sValue = [];
									for child5 in child4.childNodes:
										if child5.nodeType == Node.ELEMENT_NODE:
											sTagName5 = child5.tagName
											if (sTagName5 == (u"標識")):
												sValue += [u"[" , child5.textContent , u"]"];
											elif (sTagName5 == (u"訓")):
												sValue += [u"「" , child5.textContent , u"」"];
											elif (sTagName5 == (u"同訓字")):
												sValue += [child5.textContent];
											elif (sTagName5 == (u"同訓解")):
												sValue += [u'\n', child5.textContent];
											else:
												raise
										elif child5.nodeType == Node.TEXT_NODE:
											sValue += [child5.textContent.strip()];
										else:
											raise
									infoList.append(u"【同訓】" + u''.join(sValue));
								else:
									print >> sys.stderr, 'Tagname4 = ',
									writeunicode(sTagName4, sys.stderr)
									raise
						elif (sTagName3 == (u"熟語")):
							wordList.append(getWordContent(child3));
						else:
							print >> sys.stderr, 'Tagname3 = ',
							writeunicode(sTagName3, sys.stderr)
							raise
					if (codePoint == 0):
						writeunicode(u'%03d' % (i+1) + u", radical:" + sRadical + u", strokes:" + repr(strokes) + u" codePoint==0  char=" + sCharacter, sys.stderr);
					else:
						if (characterMap.get(sCharacter) is not None):
							writeunicode(u'%03d' % (i+1) + u", radical:" + sRadical + u", strokes:" + repr(strokes) + u" " + sCharacter + ' dup with ' + u''.join(resultList[sCharacter][:2]), sys.stderr);
					resultList.append((sCharacter, infoList));
					resultList.extend(wordList)
					charCount += 1
					wordCount += len(wordList)
				else:
					raise
	radicalMap[i] = u''.join(radicalList)

for key, value in resultList:
	writeunicode(key, sys.stdout, False)
	print '\t',
	if value[0].startswith(u'【部首】') and value[1].startswith(u'【畫數】'):
		try:
			assert value[2].startswith(u'【親字】')
		except:
			print >> sys.stderr, 'Word = ',
			writeunicode(key, sys.stderr)
			print >> sys.stderr, ' Line = ',
			writeunicode(value[2], sys.stderr)
			raise
		value = u' '.join(value[:3]) + u'\n' + u'\n'.join(value[3:])
	else:
		value = u'\n'.join(value)
	writeunicode(value.replace('\n', '\\n'))
for i in range(NUM_RADICALS):
	writeunicode(u'KO字源:' + unichr(0x2f00 + i) + u'部', sys.stdout, False)
	print '\t',
	writeunicode(radicalMap[i].replace(u'\n', u'\\n'))
print >> sys.stderr, 'Total characters:', charCount
print >> sys.stderr, 'Total words:', wordCount
print >> sys.stderr, 'Total radicals:', NUM_RADICALS

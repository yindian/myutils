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

assert __name__ == '__main__'

characterMap = {};
NUM_RADICALS = 214

for i in range(NUM_RADICALS):
	document = libxml2dom.parseString(open('%03d.xml' % (i+1), 'r').read());
	sRadical = None;
	print >> sys.stderr, 'Processing %03d.xml' % (i+1)
	for child in document.getElementsByTagName(u'部首')[0].childNodes:
		if (child.nodeType != Node.ELEMENT_NODE):
			continue;
		sTagName = (child).tagName;
		if (sTagName == (u"部首字")):
			try:
				assert len(child.textContent.strip()) == 2
			except:
				print >> sys.stderr, 'Len not 2:', child.textContent
			sRadical = u"" + child.textContent[0];
		elif (sTagName == (u"筆畫")):
			strokes = -1;
			for child2 in child.childNodes:
				if (child2.nodeType != Node.ELEMENT_NODE):
					continue;
				sTagName2 = (child2).tagName;
				if (sTagName2 == (u"畫數")):
					strokes = int(child2.textContent);
				elif (sTagName2 == (u"漢字")):
					sCharacter = None;
					codePoint = 0;
					
					infoList = [];

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
										print >> sys.stderr, 'sCharacter = ',
										writeunicode(sCharacter, sys.stderr)
										raise
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
														tmpdict = {
																u'レ':  u"\u3191",
																u'一':  u"\u3192",
																u'二':  u"\u3193",
																u'三':  u"\u3194",
																u'四':  u"\u3195",
																u'上':  u"\u3196",
																u'中':  u"\u3197",
																u'下':  u"\u3198",
															}
														for j in range(len(sType)):
															sValue2 += [tmpdict[sType[j]]];
													else:
														raise
												elif child6.nodeType == Node.TEXT_NODE:
													sValue2 += [child6.textContent.strip()];
												else:
													raise
											sValue += [u''.join(sValue2) , u"\n"];
									infoList.append(u"【解】" + u''.join(sValue));
								elif (sTagName4 == (u"解字")):
									# <標識>
									sValue = [];
									for child5 in child4.childNodes:
										if child5.nodeType == Node.ELEMENT_NODE:
											if (sTagName == (u"標識")):
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
											if (sTagName == (u"標識")):
												sValue += [u"[" , child5.textContent , u"]"];
											elif (sTagName == (u"訓")):
												sValue += [u"「" , child5.textContent , u"」"];
											elif (sTagName == (u"同訓字")):
												sValue += [child5.textContent];
											elif (sTagName == (u"同訓解")):
												sValue += [u'\n', child5.textContent];
										elif child5.nodeType == Node.TEXT_NODE:
											sValue += [child5.textContent.strip()];
										else:
											raise
									infoList.append(u"【同訓】" + u''.join(sValue));
								else:
									print >> sys.stderr, 'Tagname4 =', sTagName4
									raise
						elif (sTagName3 == (u"熟語")):
							pass
						else:
							print >> sys.stderr, 'Tagname3 =', sTagName3
							raise
					if (codePoint == 0):
						print >> sys.stderr, (u'%03d' % (i+1) + u", radical:" + sRadical + u", strokes:" + repr(strokes) + u" codePoint==0");
					else:
						if (characterMap.get(int(codePoint)) is not None):
							print >> sys.stderr, (u'%03d' % (i+1) + u", radical:" + sRadical + u", strokes:" + repr(strokes) + u" " + String.format(u"%c", codePoint));
						characterMap.__setitem__(sCharacter, infoList);
				else:
					pass

for key, value in characterMap.items():
	writeunicode(key)
	writeunicode(u'\n'.join(value).replace('\n', '\\n'))
	writeunicode('')

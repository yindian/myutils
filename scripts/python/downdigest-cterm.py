#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#发信人: yindian (Yin Dian), 信区: Script
#标  题: downdigest.py --- 用CTerm下载瀚海精华区
#发信站: 瀚海星云 (2007年06月04日14:23:31 星期一), 站内信件
#
#今天参考CTerm自带的download.py，写了这个可用于下载瀚海精华区及私人信箱的脚
#本，并成功地备份了自己的收/发信箱。小可不才，疏漏难免，欢迎大家的指正与改进。
#
#使用方法：在文章列表中将光标移到开始文章前，运行脚本即可将从光标处到最后一篇
#的文章下载到CTerm的download目录下，每篇文章一个文件，名为“编号+标题+.txt”。
#log文件见CTerm安装目录下的python.cterm.log。在CTerm v3.26 Final中试过。
#
#说明：不支持精华区的目录树递归下载。

import sys, os, string, re
from CTerm import *
from tools import *

# need:
# 0: title
# 1: writer
# 2: number
def GetTitle_(ID, need=0):
    '''分析文章标题。返回值：文章号，作者，编号'''
    #print 'in GetTitle_'
    status=GetStatus(ID)
    sub=GetSubStatus(ID)
    str1=''
    if status==SST_ARTICLE or status==SST_END or status==SST_ENTER:
        s1=GetText(ID,0)
        if s1[2:8]!='信人: ':
            return
        s2=GetText(ID,1)
        if s2[0:8]!='标  题: ':
            return
        if need==0:
            return s2[8:len(s2)].strip()
        elif need==1:
            s=s1.split()
            return s[2]
        else:
            return 0
    elif status!=SST_LIST or (sub!=SST_LIST_ARTICLE and sub!=SST_LIST_DIGEST): # list, Article list, Digest list
        print '不是文章列表.%d, %d'%(status,sub)
        return
    elif sub==SST_LIST_ARTICLE:
        n=CaretY(ID)
        str1=GetText(ID, n)
        #print 'article. caret y:%d'%n
        #>  722   nullspace    Aug 30  ● 70580.934517只青蛙70580.934517张嘴
        #>2357   nullspace    Oct  9  ◆ sd
        exp=r'^(>)?\s*(\d+)\s*([\+\*NmMgGbBrR])?\s*(\S+)\s*(\w*)\s*(\d*)(?:\.)?(?:x|@|\s+)?(● |◆ |★ |Re: )(.*[^s])\s*$'
        matchobj=re.match(exp, str1)
        if matchobj:
            #print 'str1 is "%s"'%str1
            #print  matchobj.groups()
            #return (matchobj.group(2), matchobj.group(4), matchobj.group(7), ma tchobj.group(8))  # article no.
            if need==0:
                title=''
                if matchobj.group(7)=='Re: ':
                    title+='Re: '
                title+=matchobj.group(8)
                #print title.strip()
                return title.strip()
            elif need==1:
                return matchobj.group(4)
            elif need==2:
                return int(matchobj.group(2))
        else:
            print 'str1 is "%s"'%str1
            print 'not matched'
    elif sub==SST_LIST_DIGEST:
        n=CaretY(ID)
        str1=GetText(ID, n)
        #print 'digest. caret y:%d'%n
        #->  1  [文件] 全球破解组织网址大全                   ryosaeba      [ 2002-07-24]
        #->  1 [文件] 刺客心                                 whitehawk       2005.07.31
        exp=r'^(->|\s*>)?\s*(\d+)\s*\[(.{4})\]\s*(.*?)\s*(\S+)\s*(?:\[)?\s*(\d+[-.]\d+[-.]\d+[-.]?)\s*(?:\])?\s*$'
        matchobj=re.match(exp, str1)
        if matchobj:
            #print 'str1 is "%s"'%str1
            #print  matchobj.groups()
            if need==0:
                title=matchobj.group(4)
                #print title.strip()
                return title.strip()
            elif need==1:
                return matchobj.group(5)
            elif need==2:
                return int(matchobj.group(2))
        else:
            print 'str1 is "%s"'%str1
            print 'not matched'
    return 0

def dropCR(text):
    str_list=text.split('\n')
    linecount=len(str_list)
    reexp=re.compile(r'^\s*$')
    for i in range(linecount):
        rematch=re.match(reexp,str_list[-(i+1)])
        if not rematch:
            break
    return string.join(str_list[0:linecount-i], '\n')

# 下载文章
# savetype:
# 0: 文本
# 1: ansi
def copyDigest(ID, savetype=0, quitcmd='q'):
    #返回光标所在处的文章内容
    global GetTitle_
    data=''
    title=''
    lastline=''
    status=GetStatus(ID)
    sub=GetSubStatus(ID)
    statuslist = ('SST_UNKNOWN', 'SST_MENU', 'SST_LIST', 'SST_ARTICLE', 'SST_END', 'SST_CHATROOM', 'SST_TALK', 'SST_WRITE', 'SST_INPUT', 'SST_ENTER', 'SST_MESSAGE', 'SST_DIGEST_UNKNOWN', 'SST_ANY', 'SST_HOT', 'SST_USER')
    sublist = ('SST_LIST_ARTICLE', 'SST_LIST_BOARD', 'SST_LIST_DIGEST', 'SST_LIST_USER', 'SST_LIST_UNKWON')
    print 'status: %s, substatus: %s' % (statuslist[status], sublist[sub-100])
    if status==SST_LIST and (sub==SST_LIST_DIGEST or sub==SST_LIST_ARTICLE):
        title=GetTitle_(ID)
        print 'send r'
        SendString(ID,'r')
        WaitFor(ID,bAutoEnter=False,timeout=0.04)
    elif status==SST_ARTICLE or status==SST_END or status==SST_ENTER:
        title=GetTitle_(ID)
    else:
        return (None,None)
    # now: SST_ARTICLE or SST_END or SST_ENTER
    status=0
    while True:
        status=status or GetStatus(ID)
        if status==SST_ARTICLE:
            #print 'SST_ARTICLE'
            if GetText(ID,0)==lastline:
                print 'skip dup line',lastline.rstrip()
                if savetype==0:
                    data+=GetText(ID,1,22)
                else:
                    data+=GetAttrText(ID,1,22)
            else:
                if savetype==0:
                    data+=GetText(ID,0,22)
                else:
                    data+=GetAttrText(ID,0,22)
            data+='\n'
            lastline=GetText(ID,22)
            SendString(ID,' ')
            WaitFor(ID,bAutoEnter=False,timeout=0.01)
            sys.stdout.flush()
            status=0
        elif status==SST_END or status==SST_ENTER:
            #print status
            # 查找与上一屏的重复行；这也许可以用difflib来做
            start=0
            for i in range(22):
                s=GetText(ID,i)
                if s==lastline:
                    start=i+1
                    break
            if savetype==0:
                data+=GetText(ID,start,22)
            else:
                data+=GetAttrText(ID,start,22)
            SendString(ID, quitcmd)
            break
        else:
            print 'wrong status. status: %s, substatus: %s' % (statuslist[status], sublist[sub-100])
            print 'current lastline=', GetText(ID,22)
            print 'treat it like still in article mode'
            status=SST_ARTICLE
    return (title,data)

#main
ID=long(sys.argv[0])
if not ID:
    sys.exit(1)
print '\nNow start...'
num=initnum=GetTitle_(ID,2)
while True:
    title,data=copyDigest(ID,0,'e')
    if data:
        data=string.translate(dropCR(data), string.maketrans('',''), '\r')
        data='\n'.join(map(string.rstrip, data.split('\n')))
        print title
        if title and type(title)==str:
            destdir='download'
            try:
                os.mkdir(destdir)
            except OSError:
                pass
            title=re.sub(r'[\:\?\*\\\/\>\<]','_',title)
            try:
                f=file(destdir+'\\'+'%4d '%num+title+'.txt', 'wt') # U?
                f.write(data)
                f.close()
            except IOError, errinfo:
                print title+'.txt'+': '+errinfo[1]
    else:
        print 'error: no data'
    WaitFor(ID,SST_LIST,bAutoEnter=False,timeout=0.04)
    SendString(ID,'j')
    WaitFor(ID,SST_LIST,bAutoEnter=False,timeout=0.02)
    num=GetTitle_(ID,2)
    print 'num=%d'%num
    if num<=initnum:
        break
    sys.stdout.flush()
sys.stdout.flush()
#--
#※ 修改:·yindian 于 06月04日14:28:57·[FROM: 202.38.70.5]
#※ 来源:·瀚海星云 bbs.ustc.edu.cn·[FROM: 202.38.70.5]

import os, sys, zlib, time, datetime, re
from struct import *
import pdb, traceback

def trimBaike(s):
    s = s.replace(b'<br>', b'\\n').replace(b'&amp;', b'&').replace(b'&nbsp;', b' ')\
        .replace(b'&gt;', b'>').replace(b'&lt;', b'<')\
        .replace(b'&amp;', b'&').replace(b'&quot;', b'"')
    s = re.sub(b'\[\[(.*?)\]\]', b'//STEHYPERLINK=\g<1>\1//', s)   #把[[]]变成STE超链接
    s = re.sub(b'<A HREF="entry://(.*?)/">.*?</A>', b'//STEHYPERLINK=\g<1>\1//', s)
    return s
    
block_size = 16 * 1024

def unste(s):    
    return s.replace(b'//STEHYPERLINK=', b'[[').replace(b'\1//', b']]')#把STE超链接还原成[[]]
                    
class ZDic:
    def __init__(self, compressFlag = 2, recordSize = 0x4000):
        "初始化ZDic类，默认为Zlib压缩方式，16K页面大小"
        #PDB文件头
        self.PDBHeaderStructString = '>32shhLLLlll4s4sllH'           
        self.PDBHeaderStructLength = calcsize(self.PDBHeaderStructString)
        self.PDBHeaderPadding = b'\0\0'
        self.creatorID = 'Kdic'
        self.pdbType = 'Dict'
        self.maxWordLen = 32
        self.recordSize = recordSize        
        self.compressFlag = compressFlag
        
        #info, block, index, block offset, index offset
        self.infoStruct = '>2HLL4x'
        self.infoLen = calcsize(self.infoStruct)
        self.num = 0

        self.index = b''
        self.indexLen = []
        self.offset = []

        self.blen = [self.infoLen, 0, 0, 0, 0]
        self.len = len(self.blen)
        self.bOffset = self.PDBHeaderStructLength + 8*self.len + len(self.PDBHeaderPadding)
        self.size = 0
    
    def packPalmDate(self, variable=None):
        PILOT_TIME_DELTA = 2082844800        
        variable = variable or datetime.datetime.now()
        return int(time.mktime(variable.timetuple()) + PILOT_TIME_DELTA)
        
    def packPDBHeader(self):
        head = pack(self.PDBHeaderStructString,
                    self.pdbName, 0, 0,
                    self.packPalmDate(), 0, 0, 0, 0, 0,
                    self.pdbType, self.creatorID, 0, 0, self.len)
        return head

    def packInfoRecord(self):
        head = b''
        uid = 0
        offset = self.bOffset
        for i in self.blen:
            head += pack('>2L', offset, uid) 
            offset += i
            uid += 1
        head += self.PDBHeaderPadding
        head += pack(self.infoStruct, 1, self.compressFlag, self.num, self.size)
        return head

    def toPDB(self,path):        
        t = open(path,'rb+')
        t.write(self.packPDBHeader())
        t.write(self.packInfoRecord())
        t.close()   
    
    def fromPDB(self, pathi, patho):
        f = open(pathi, 'rb')
        t = open(patho, 'wb')
        head = f.read(self.PDBHeaderStructLength)
        d = {}
        self.pdbName, d[0], d[1], d['time'], d[2], d[3], d[4], d[5], d[6], \
                self.pdbType, self.creatorID, d[7], d[8], self.len = \
                unpack(self.PDBHeaderStructString, head)
        lastoffset = 0
        for i in range(len(self.blen)):
            head = f.read(8)
            offset, uid = unpack('>2L', head)
            if i > 0:
                self.blen[i-1] = offset - lastoffset
            lastoffset = offset
        self.blen[-1] = self.blen[-2] - 4
        head = f.read(len(self.PDBHeaderPadding))
        head = f.read(self.infoLen)
        d[1], self.compressFlag, self.num, self.size = \
                unpack(self.infoStruct, head)
        #print(self.__dict__)
        f.seek(sum(self.blen[:2], self.bOffset))
        self.index = f.read(self.blen[2])
        #t.write(self.index.replace(b'\0', b'\n'))
        #print(self.index[:256].replace(b'\0', b'\n'))
        for i in range(self.num + 1):
            self.offset.append(unpack('>L', f.read(4))[0])
        for i in range(self.num):
            self.indexLen.append(unpack('>L', f.read(4))[0])
        assert f.tell() == self.size
        f.seek(self.offset[0])
        longline = []
        lineno = 0
        def sameword(last, line):
            if last.startswith(b'Air Jordan 4'):
                pdb.set_trace()
            if line.find(b'\t') < last.find(b'\t') or 32 >= line.find(
                    b'\t') > last.find(b'\t'):
                return False
            if line.find(b'\t') > 32 and not line.startswith(last[:last.find(
                b'\t')]):
                return False
            if last.find(b'\t') == 32 and line.startswith(last[:last.find(
                b'\t')]):
                return True
            p = last.rfind(b' ', 0, last.index(b'\t'))
            if p < 0 or not line.startswith(last[:p]):
                return False
            q = line.rfind(b' ', 0, line.index(b'\t'))
            if p != q:
                return False
            try:
                int(last[p+1:last.index(b'\t')])
                int(line[q+1:line.index(b'\t')])
            except:
                return False
            return True
        for i in range(self.num):
            block = f.read(self.offset[i+1] - self.offset[i])
            block = zlib.decompress(block)
            try:
                if block.find(b'\0') >= 0 and longline:
                    if not sameword(longline[-1], block[:block.find(b'\n')]):
                        print('Improper \\0 in %s' % (block[:block.find(b'\t')]
                            .decode('gbk', 'ignore'),), file=sys.stderr)
                        p = block.find(b'\0')
                        block = block[:p] + block[p+1:]
                    else:
                        p = block.index(b'\t')
                        assert chr(block[p-1]).isdigit()
                        q = block.rindex(b' ', 0, p)
                        num = int(block[q+1:p])
                        wholeword = block[:q]
                        p = block.find(b'\0')
                        longline.append(block[:p])
                        while len(longline) > num:
                            print('Ambiguous word %s vs %s' % (longline[0][:
                                longline[0].find(b'\t')].decode('gbk','ignore'),
                                longline[-1][:longline[-1].find(b'\t')]
                                .decode('gbk', 'ignore'),), file=sys.stderr)
                            word, mean = longline[0].split(b'\t', 1)
                            t.write(word)
                            t.write(b'\t')
                            t.write(unste(mean))
                            if not mean.endswith(b'\n'): t.write(b'\n')
                            del longline[0]
                        for j in range(num):
                            word, mean = longline[j].split(b'\t', 1)
                            if j < num-1:
                                assert len(word) <= 32
                            lineno += 1
                            t.write(wholeword+ (' %d' % (j+1,)).encode('ascii'))
                            t.write(b'\t')
                            t.write(unste(mean))
                        block = block[p+1:]
                        longline = []
                if not block:
                    continue
                lines = []
                for line in block.split(b'\n\n'):
                    if not line or line in (b'\0', b'\n'):
                        continue
                    if line.find(b'\t') >= 0:
                        lines.append(line)
                    elif not lines:
                        if longline:
                            longline[-1] += line
                        else:
                            lines.append(line.rstrip(b'\n\0'))
                    else:
                        print('Append %s to %s' % (line[:32].decode('gbk',
                            'ignore'), lines[-1][:32].decode('gbk', 'ignore')),
                            file=sys.stderr)
                        lines[-1] += line
                if longline and (len(lines) > 1 or not sameword(
                    longline[-1], lines[0])):
                    for line in longline:
                        lineno += 1
                        try:
                            mean = b''
                            word, mean = line.split(b'\t', 1)
                            t.write(word)
                            t.write(b'\t')
                            t.write(unste(mean))
                        except:
                            print('No tab on line %d'%(lineno,),file=sys.stderr)
                            t.write(unste(line))
                        if not mean.endswith(b'\n'): t.write(b'\n')
                    longline = []
                for line in lines[:-1]:
                    lineno += 1
                    word, mean = line.split(b'\t', 1)
                    t.write(word)
                    t.write(b'\t')
                    t.write(unste(mean))
                    if not mean.endswith(b'\n'): t.write(b'\n')
                if lines[-1]:
                    longline.append(lines[-1])
            except:
                traceback.print_exc()
                pdb.set_trace()
                raise
        t.close()
        f.close()

    def from25(self, pathi, patho):
        t = open(patho, 'wb')        
        offset = self.bOffset + self.infoLen
        indexLen = 0
        count = 0
        t.write(pack('%dx' % offset))
        self.offset = [offset]

        for path in pathi:
            f = open(path, 'rb')
            f.seek(0x56)
            blockoffset = unpack('>L', f.read(4))[0]
            f.seek(blockoffset)
            block = f.read(block_size)
            while block:
                t.write(block)
                block = f.read(block_size)
            f.seek(0x4E)
            f.seek(unpack('>L', f.read(4))[0])
            f.seek(4, os.SEEK_CUR)
            blocknum = unpack('>H', f.read(2))[0]
            self.compressFlag = unpack('>H', f.read(2))[0]
            count += blocknum
            f.seek(8, os.SEEK_CUR)
            blocklen = unpack('>%dH' % blocknum, f.read(2*blocknum))
            for i in blocklen:
                offset += i
                self.offset.append(offset)
            if blockoffset >= f.tell():
                self.index+=f.read(blockoffset - f.tell())
            f.close()
        self.blen = [self.infoLen,
                     offset - self.bOffset - self.infoLen,
                     len(self.index),
                     4 * count + 4, 4 * count]
        self.num = count
        self.size = sum(self.blen, self.bOffset)
        t.write(self.index)
        for i in self.offset:
            t.write(pack('>L', i))
        indexoffset = 0
        for i in range(count):            
            indexoffset = self.index.index(b'\0', indexoffset) + 1
            t.write(pack('>L', offset + indexoffset))
            indexoffset = self.index.index(b'\0', indexoffset) + 1
        t.close()
        
    def fromTXT(self, path, patho):
        "从TXT中读取数据"
        f=open(path, 'rb')
        t=open(patho, 'wb')        
        offset = self.bOffset + self.infoLen
        indexLen = 0
        count = 0
        t.write(pack('%dx' % offset))
        self.offset = [offset]

        block = b''
        firstWord = b''
        lastWord = b''
        for line in f:
            line = line.rstrip() + b'\n'
            word, mean = line.split(b'\t', 1)
            #mean = trimBaike(mean)
            #line = word + b'\t' + mean + b'\n'
            if not block:
                firstWord = word
                lastWord = word
            if len(block) + len(line) < self.recordSize:
                block += line
                lastWord = word
            else:
                if block:
                    block = zlib.compress(block, 9)
                    t.write(block)
                    index = firstWord[:32] + b'\0' + lastWord[:32] + b'\0'                    
                    self.indexLen.append(indexLen + len(firstWord[:32]) + 1)
                    self.index += index
                    indexLen += len(index)
                    offset += len(block)
                    self.offset.append(offset)
                    count += 1
                    block = b''
                if len(line) < self.recordSize:
                    block = line
                    firstWord = word
                    lastWord = word
                else:
                    i = 0
                    while mean:
                        i += 1
                        firstWord = word + (' %d' % i).encode('ascii')
                        lastWord = firstWord
                        blen = self.recordSize - len(firstWord) - 3
                        if blen > len(mean):
                            block = firstWord + b'\t' + mean + b'\0' 
                            mean = b''
                        else:
                            breakIndex = mean.rfind(b'\\n', 0, blen)
                            if breakIndex == -1:
                                breakIndex = blen
                            else:
                                blen = breakIndex + 2                            
                            block = firstWord[:32] + b'\t' + mean[:breakIndex] + b'\n'
                            block = zlib.compress(block, 9)
                            t.write(block)
                            index = firstWord[:32] + b'\0' + lastWord[:32] + b'\0'                    
                            self.indexLen.append(indexLen + len(firstWord[:32]) + 1)
                            self.index += index
                            indexLen += len(index)
                            offset += len(block)
                            self.offset.append(offset)
                            count += 1
                            block = b''
                            mean = mean[blen:]
        if block:
            block = zlib.compress(block, 9)
            t.write(block)
            index = firstWord[:32] + b'\0' + lastWord + b'\0'                    
            self.indexLen.append(indexLen + len(firstWord[:32]) + 1)
            self.index += index
            indexLen += len(index)
            offset += len(block)
            self.offset.append(offset)
            count += 1
            block = b''

        self.blen = [self.infoLen,
                     offset - self.bOffset - self.infoLen,
                     indexLen,
                     4 * count + 4, 4 * count]
        
        self.num = count
        self.size = sum(self.blen, self.bOffset)
        t.write(self.index)
        for i in self.offset:
            t.write(pack('>L', i))
        for i in self.indexLen:
            t.write(pack('>L', offset+i))
            
        f.close()
           
def log(msg):
    "打印日志"
    print ('[%s]%s'%(time.strftime('%X'), msg))
    
if __name__ == '__main__':   
    argv = sys.argv[1:]
    if len(argv) < 2:
        log('语法: [-b|-t] 文件1 文件2') #参数错误时给出语法提示
    else:
        pathi = argv[:-1]
        patho = argv[-1]
        s = time.time() #记录开始时间
        log('读入...')
        app = ZDic()    #初使化ZDic数据结构
        app.pdbName = os.path.splitext(os.path.basename(patho))[0].encode('gbk')
        if pathi[0] == '-b':
        	app.fromTXT(pathi[1], patho)
        elif pathi[0] == '-t':
        	app.fromPDB(pathi[1], patho)
        else:
        	app.from25(pathi, patho)
        log('保存...')
        if pathi[0] != '-t':
            app.toPDB(patho)
        cost = time.time() - s #计算花费时间
        log('成功! 花费 %02d分%02d秒。\n' % (cost/60, cost%60))        



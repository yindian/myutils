#!/usr/bin/env python3
# input yong mb or filtered cin using:
#  awk '/^%chardef begin/{f=1;next};f{if($1==a){b=b " " $2}else{if(a)printf("%s %s\n",a,b);a=$1;b=$2}}'
import sys
name = None
first = True
for line in sys.stdin:
    ar = line.rstrip().split(' ')
    if len(ar) > 1 and ar[0].isalpha():
        br = []
        i = 1
        while i < len(ar):
            if not ar[i]:
                i += 1
                continue
            c = ord(ar[i][0])
            if 0x3400 <= c < 0xA000 or 0xE000 <= c < 0xFB00 or 0x20000 <= c < 0x30000 or 0xF0000 <= c:
                i += 1
            else:
                #br.append(ar.pop(i))
                br.append(ar[i])
                if ar[i].startswith('$'):
                    del ar[i]
                    continue
                ar[i] = '(%s)' % (ar[i], )
                i += 1
        if br:
            if len(ar) == 1:
                continue
            line = '%s\n' % (' '.join(ar), )
            #br.insert(0, ar[0])
            #if len(ar) > 1:
            #    line = '%s\n`%s\n' % (' '.join(ar), ' '.join(br))
            #else:
            #    line = '`%s\n' % (' '.join(br), )
    else:
        p = line.find('name=')
        if p >= 0:
            name = line[p+5:].strip()
        continue
    if first:
        first = False
        sys.stdout.write(chr(0xFEFF))
        sys.stdout.write('''\
; [cmd:RefCode]
[cmd:RemoveAll]
[cmd:Info=%s]
;------------------------------
''' % (name,))
    sys.stdout.write(line)

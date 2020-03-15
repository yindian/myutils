#!/usr/bin/env python
from __future__ import print_function
import sys
import struct
import io

gbkpua2unimap = dict([[int(x, 16) for x in s.split()] for s in '''\
E7C7 1E3F
E7C8 01F9
E7E7 303E
E7E8 2FF0
E7E9 2FF1
E7EA 2FF2
E7EB 2FF3
E7EC 2FF4
E7ED 2FF5
E7EE 2FF6
E7EF 2FF7
E7F0 2FF8
E7F1 2FF9
E7F2 2FFA
E7F3 2FFB
E815 2E81
E816 20087
E817 20089
E818 200CC
E819 2E84
E81A 3473
E81B 3447
E81C 2E88
E81D 2E8B
E81E 9FB4
E81F 359E
E820 361A
E821 360E
E822 2E8C
E823 2E97
E824 396E
E825 3918
E826 9FB5
E827 39CF
E828 39DF
E829 3A73
E82A 39D0
E82B 9FB6
E82C 9FB7
E82D 3B4E
E82E 3C6E
E82F 3CE0
E830 2EA7
E831 215D7
E832 9FB8
E833 2EAA
E834 4056
E835 415F
E836 2EAE
E837 4337
E838 2EB3
E839 2EB6
E83A 2EB7
E83B 2298F
E83C 43B1
E83D 43AC
E83E 2EBB
E83F 43DD
E840 44D6
E841 4661
E842 464C
E843 9FB9
E844 4723
E845 4729
E846 477C
E847 478D
E848 2ECA
E849 4947
E84A 497A
E84B 497D
E84C 4982
E84D 4983
E84E 4985
E84F 4986
E850 499F
E851 499B
E852 49B7
E853 49B6
E854 9FBA
E855 241FE
E856 4CA3
E857 4C9F
E858 4CA0
E859 4CA1
E85A 4C77
E85B 4CA2
E85C 4D13
E85D 4D14
E85E 4D15
E85F 4D16
E860 4D17
E861 4D18
E862 4D19
E863 4DAE
E864 9FBB
'''.splitlines()])
assert __name__ == '__main__'

with open(sys.argv[1], 'rb') as f:
    lines = f.readlines()
    chet = u'\u5207'
    usep = u'\u250a'
    sep = usep.encode('utf-8')
    out = io.BytesIO()
    d = {}
    dd = {}
    dl = []
    if lines[0].find(sep) >= 0:
        assert lines[0].count(sep) == 22
        specials = {
                179:    'chryi', # was 'chjyi',
                4001:   'nrungx',
                4002:   'njah',
                4003:   'khimh',
                4004:   'chuan',
                4015:   'gaih',
                4006:   'puot',
                4007:   'ty',
                4008:   'chrah',
                4009:   'thauh',
                }
        for line in lines:
            try:
                line = line.rstrip().decode('utf-8')
                line = line.encode('utf-16le').decode('utf-16le', 'ignore')
                ar = line.split(usep)
            except UnicodeDecodeError: # broken surrogate pair in Python 3 
                line = line.rstrip().decode('utf-8', 'ignore')
                ar = line.split(usep)
                print('Invalid UTF-8 bytes ignored for %s %s' % (
                    ar[0],
                    ar[10],
                    ), file=sys.stderr)
            try:
                if not ar[0].isdigit(): # header
                    assert not d
                    continue
                for i in range(len(ar)):
                    s = ar[i]
                    if s.startswith(u'"'):
                        assert s.endswith(u'"')
                        ar[i] = s[1:-1].replace(u'""', u'"')
                key = ar[10] or specials[int(ar[0])]
                line = u'%s\t%s %s%s %s%s%s%s%s%s %s%s %s%s\\n%s' % (
                        key,
                        ar[1],
                        ar[7],
                        ar[7] and chet,
                        ar[8],
                        ar[4],
                        ar[3],
                        ar[6],
                        ar[5],
                        ar[2],
                        ar[13] and u'\u62fc\u97f3:',
                        ar[13],
                        ar[22] and u'\u5e73\u6c34\u97f5:',
                        ar[22],
                        ar[9],
                        )
                if ar[12]:
                    line += u'\\n' + ar[12]
                if key in d:
                    print('Duplicated key %s' % (
                        key,
                        ), file=sys.stderr)
                    d[key] = u'%s\t%s\\n\\n%s' % (
                            key,
                            d[key][len(key)+1:],
                            line[len(key)+1:],
                            )
                else:
                    d[key] = line
                    dl.append(key)
                s = ar[9]
                for i in range(len(s)):
                    c = s[i]
                    o = ord(c)
                    if 0xD800 <= o < 0xDC00:
                        o = ord(s[i+1])
                        assert 0xDC00 <= o < 0xE000
                        c += s[i+1]
                    elif 0xDC00 <= o < 0xE000:
                        # handled in above case
                        continue
                    elif o < 0x80 or 0xFF00 <= o < 0x10000:
                        continue
                    else:
                        assert o < 0x110000
                        assert o >= 0x2E80
                    dd.setdefault(c, set()).add(key)
                    if len(c) == 1 and 0xE000 <= o < 0xF900:
                        try:
                            o = gbkpua2unimap[o]
                            if o < 0x10000:
                                cc = struct.pack('<H', o).decode('utf-16le')
                            else:
                                o -= 0x10000
                                cc = struct.pack('<2H',
                                        0xD800 | (o >> 10),
                                        0xDC00 | (o & 0x3FF),
                                        ).decode('utf-16le')
                            dd.setdefault(cc, set()).add(key)
                        except KeyError:
                            print('Found PUA U+%04X for %s' % (
                                o,
                                key,
                                ), file=sys.stderr)
            except:
                print('Error processing %s %s' % (
                    ar[0],
                    ar[10],
                    ), file=sys.stderr)
                #print(usep.join(ar), file=sys.stderr)
                raise
        for key in dl:
            line = d[key]
            out.write(line.encode('utf-8'))
            out.write(b'\n')
    else:
        assert False
    try:
        sys.stdout.write(out.getvalue())
    except TypeError: # Python 3
        sys.stdout.buffer.write(out.getvalue())
    out.close()
    out = io.BytesIO()
    no_apos = lambda s: s.find("'") >= 0 and (s.replace("'", '') + "'") or s
    uniord = lambda c: len(c) == 1 and ord(c) or (
            ((ord(c[0]) & 0x3FF) << 10) | (ord(c[1]) & 0x3FF))
    for c in sorted(dd.keys(), key=uniord):
        out.write((u'%s\t%s\n' % (
            c,
            u', '.join(sorted(dd[c], key=no_apos)),
            )).encode('utf-8'))
    try:
        sys.stdout.write(out.getvalue())
    except TypeError: # Python 3
        sys.stdout.buffer.write(out.getvalue())

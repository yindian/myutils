#!/usr/bin/env python
from __future__ import print_function
import sys
import struct
import io
import operator
from checkpy import gy2py

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

sjenglst = u'''\
\u5E6B \u6EC2 \u4E26 \u660E \u7AEF \u900F \u5B9A \u6CE5 \u4F86
\u77E5 \u5FB9 \u6F84 \u5A18 \u7CBE \u6E05 \u5F9E \u5FC3 \u90AA
\u838A \u521D \u5D07 \u751F \u4FDF \u7AE0 \u660C \u5E38 \u66F8 \u8239 \u65E5
\u898B \u6EAA \u7FA4 \u7591 \u66C9 \u5323 \u5F71 \u4E91 \u4EE5
'''.split()
assert len(sjenglst) == 38

miuklst = u'''\
\u6771 \u51AC \u937E \u6C5F \u652F \u8102 \u4E4B \u5FAE \u9B5A \u865E
\u6A21 \u9F4A \u4F73 \u7686 \u7070 \u548D \u771E \u8AC4 \u81FB \u6587
\u6B23 \u5143 \u9B42 \u75D5 \u5BD2 \u6853 \u522A \u5C71 \u5148 \u4ED9
\u856D \u5BB5 \u80B4 \u8C6A \u6B4C \u6208 \u9EBB \u967D \u5510 \u5E9A
\u8015 \u6E05 \u9752 \u84B8 \u767B \u5C24 \u4FAF \u5E7D \u4FB5 \u8983
\u8AC7 \u9E7D \u6DFB \u54B8 \u929C \u56B4 \u51E1 \u61C2 \u816B \u8B1B
\u7D19 \u65E8 \u6B62 \u5C3E \u8A9E \u9E8C \u59E5 \u85BA \u87F9 \u99ED
\u8CC4 \u6D77 \u8EEB \u6E96 \u543B \u96B1 \u962E \u6DF7 \u5F88 \u65F1
\u7DE9 \u6F78 \u7522 \u9291 \u736E \u7BE0 \u5C0F \u5DE7 \u6667 \u54FF
\u679C \u99AC \u990A \u8569 \u6897 \u803F \u975C \u8FE5 \u62EF \u7B49
\u6709 \u539A \u9EDD \u5BD1 \u611F \u6562 \u7430 \u5FDD \u513C \u8C4F
\u6ABB \u8303 \u9001 \u5B8B \u7528 \u7D73 \u5BD8 \u81F3 \u5FD7 \u672A
\u5FA1 \u9047 \u66AE \u973D \u796D \u6CF0 \u5366 \u602A \u592C \u968A
\u4EE3 \u5EE2 \u9707 \u7A15 \u554F \u712E \u9858 \u6141 \u6068 \u7FF0
\u63DB \u8AEB \u8947 \u9730 \u7DDA \u562F \u7B11 \u6548 \u53F7 \u7B87
\u904E \u79A1 \u6F3E \u5B95 \u6620 \u8ACD \u52C1 \u5F91 \u8B49 \u5D9D
\u5BA5 \u5019 \u5E7C \u6C81 \u52D8 \u95DE \u8C54 \U0002354A \u91C5 \u9677
\u9451 \u68B5 \u5C4B \u6C83 \u71ED \u89BA \u8CEA \u8853 \u6ADB \u7269
\u8FC4 \u6708 \u6C92 \u66F7 \u672B \u9EE0 \u938B \u5C51 \u859B \u85E5
\u9438 \u964C \u9EA5 \u6614 \u932B \u8077 \u5FB7 \u7DDD \u5408 \u76CD
\u8449 \u6017 \u6D3D \u72CE \u696D \u4E4F 
'''.split()
assert len(miuklst) == 206

try:
    reduce
except NameError:
    from functools import reduce
miuk2sjep = dict(reduce(operator.add, [reduce(operator.add,
    [[(a[i], a[0])] for i in range(1, len(a))]) for a in [
    s.split() for s in u'''\
\u901A\t\u6771\t\u8463\t\u9001\t\u5C4B
\u901A\t\u51AC\t\u6E69\t\u5B8B\t\u6C83
\u901A\t\u937E\t\u816B\t\u7528\t\u71ED
\u6C5F\t\u6C5F\t\u8B1B\t\u7D73\t\u89BA
\u6B62\t\u652F\t\u7D19\t\u5BD8\t
\u6B62\t\u8102\t\u65E8\t\u81F3\t
\u6B62\t\u4E4B\t\u6B62\t\u5FD7\t
\u6B62\t\u5FAE\t\u5C3E\t\u672A\t
\u9047\t\u9B5A\t\u8A9E\t\u5FA1\t
\u9047\t\u865E\t\u9E8C\t\u9047\t
\u9047\t\u6A21\t\u59E5\t\u66AE\t
\u87F9\t\u9F4A\t\u85BA\t\u973D\t
\u87F9\t\t\t\u796D\t
\u87F9\t\t\t\u6CF0\t
\u87F9\t\u4F73\t\u87F9\t\u5366\t
\u87F9\t\u7686\t\u99ED\t\u602A\t
\u87F9\t\t\t\u592C\t
\u87F9\t\u7070\t\u8CC4\t\u968A\t
\u87F9\t\u548D\t\u6D77\t\u4EE3\t
\u87F9\t\t\t\u5EE2\t
\u81FB\t\u771E\t\u8EEB\t\u9707\t\u8CEA
\u81FB\t\u8AC4\t\u6E96\t\u7A15\t\u8853
\u81FB\t\u81FB\t\U0002791B\t\u6AEC\t\u6ADB
\u81FB\t\u6587\t\u543B\t\u554F\t\u7269
\u81FB\t\u6B23\t\u96B1\t\u712E\t\u8FC4
\u5C71\t\u5143\t\u962E\t\u9858\t\u6708
\u81FB\t\u9B42\t\u6DF7\t\u6141\t\u6C92
\u81FB\t\u75D5\t\u5F88\t\u6068\t\u9EA7
\u5C71\t\u5BD2\t\u65F1\t\u7FF0\t\u66F7
\u5C71\t\u6853\t\u7DE9\t\u63DB\t\u672B
\u5C71\t\u522A\t\u6F78\t\u8AEB\t\u9EE0
\u5C71\t\u5C71\t\u7522\t\u8947\t\u938B
\u5C71\t\u5148\t\u9291\t\u9730\t\u5C51
\u5C71\t\u4ED9\t\u736E\t\u7DDA\t\u859B
\u6548\t\u856D\t\u7BE0\t\u562F\t
\u6548\t\u5BB5\t\u5C0F\t\u7B11\t
\u6548\t\u80B4\t\u5DE7\t\u6548\t
\u6548\t\u8C6A\t\u6667\t\u53F7\t
\u679C\t\u6B4C\t\u54FF\t\u7B87\t
\u679C\t\u6208\t\u679C\t\u904E\t
\u5047\t\u9EBB\t\u99AC\t\u79A1\t
\u5B95\t\u967D\t\u990A\t\u6F3E\t\u85E5
\u5B95\t\u5510\t\u8569\t\u5B95\t\u9438
\u6897\t\u5E9A\t\u6897\t\u6620\t\u964C
\u6897\t\u8015\t\u803F\t\u8ACD\t\u9EA5
\u6897\t\u6E05\t\u975C\t\u52C1\t\u6614
\u6897\t\u9752\t\u8FE5\t\u5F91\t\u932B
\u66FE\t\u84B8\t\u62EF\t\u8B49\t\u8077
\u66FE\t\u767B\t\u7B49\t\u5D9D\t\u5FB7
\u6D41\t\u5C24\t\u6709\t\u5BA5\t
\u6D41\t\u4FAF\t\u539A\t\u5019\t
\u6D41\t\u5E7D\t\u9EDD\t\u5E7C\t
\u6DF1\t\u4FB5\t\u5BD1\t\u6C81\t\u7DDD
\u54B8\t\u8983\t\u611F\t\u52D8\t\u5408
\u54B8\t\u8AC7\t\u6562\t\u95DE\t\u76CD
\u54B8\t\u9E7D\t\u7430\t\u8C54\t\u8449
\u54B8\t\u6DFB\t\u5FDD\t\u3B87\t\u6017
\u54B8\t\u54B8\t\u8C4F\t\u9677\t\u6D3D
\u54B8\t\u929C\t\u6ABB\t\u9451\t\u72CE
\u54B8\t\u56B4\t\u513C\t\u91C5\t\u696D
\u54B8\t\u51E1\t\u68B5\t\u8303\t\u4E4F
'''.splitlines()]]))
miukaliases = dict([s.split() for s in u'''\
\u61C2\t\u8463
\U0002354A\t\u3B87
'''.splitlines()])
miuk2sjep.update([(alias, miuk2sjep[k]) for alias,k in miukaliases.items()])
assert len(set(miuk2sjep.values())) == 16

miuk2bs = dict(reduce(operator.add, [reduce(operator.add,
    [[(a[i], a[0])] for i in range(1, len(a))]) for a in [
    s.split() for s in u'''\
\u6771\t\u6771
\u51AC\t\u51AC \u937E
\u6C5F\t\u6C5F
\u652F\t\u652F \u8102 \u4E4B
\u5FAE\t\u5FAE
\u9B5A\t\u9B5A
\u865E\t\u865E \u6A21
\u9F4A\t\u9F4A
\u4F73\t\u4F73 \u7686
\u7070\t\u7070 \u548D
\u771E\t\u771E \u8AC4 \u81FB
\u6587\t\u6587 \u6B23
\u5143\t\u5143 \u9B42 \u75D5
\u5BD2\t\u5BD2 \u6853
\u522A\t\u522A \u5C71
\u5148\t\u5148 \u4ED9
\u856D\t\u856D \u5BB5
\u80B4\t\u80B4
\u8C6A\t\u8C6A
\u6B4C\t\u6B4C \u6208
\u9EBB\t\u9EBB
\u967D\t\u967D \u5510
\u5E9A\t\u5E9A \u8015 \u6E05
\u9752\t\u9752
\u84B8\t\u84B8 \u767B
\u5C24\t\u5C24 \u4FAF \u5E7D
\u4FB5\t\u4FB5
\u8983\t\u8983 \u8AC7
\u9E7D\t\u9E7D \u6DFB
\u54B8\t\u54B8 \u929C \u56B4 \u51E1
\u8463\t\u61C2
\u816B\t\u816B
\u8B1B\t\u8B1B
\u7D19\t\u7D19 \u65E8 \u6B62
\u5C3E\t\u5C3E
\u8A9E\t\u8A9E
\u9E8C\t\u9E8C \u59E5
\u85BA\t\u85BA
\u87F9\t\u87F9 \u99ED
\u8CC4\t\u8CC4 \u6D77
\u8EEB\t\u8EEB \u6E96
\u543B\t\u543B \u96B1
\u962E\t\u962E \u6DF7 \u5F88
\u65F1\t\u65F1 \u7DE9
\u6F78\t\u6F78 \u7522
\u9291\t\u9291 \u736E
\u7BE0\t\u7BE0 \u5C0F
\u5DE7\t\u5DE7
\u6667\t\u6667
\u54FF\t\u54FF \u679C
\u99AC\t\u99AC
\u990A\t\u990A \u8569
\u6897\t\u6897 \u803F \u975C
\u8FE5\t\u8FE5 \u62EF \u7B49
\u6709\t\u6709 \u539A \u9EDD
\u5BD1\t\u5BD1
\u611F\t\u611F \u6562
\u7430\t\u7430 \u5FDD \u513C
\u8C4F\t\u8C4F \u6ABB \u8303
\u9001\t\u9001
\u5B8B\t\u5B8B \u7528
\u7D73\t\u7D73
\u5BD8\t\u5BD8 \u81F3 \u5FD7
\u672A\t\u672A
\u5FA1\t\u5FA1
\u9047\t\u9047 \u66AE
\u973D\t\u973D \u796D
\u6CF0\t\u6CF0
\u5366\t\u5366 \u602A \u592C
\u968A\t\u968A \u4EE3 \u5EE2
\u9707\t\u9707 \u7A15
\u554F\t\u554F \u712E
\u9858\t\u9858 \u6141 \u6068
\u7FF0\t\u7FF0 \u63DB
\u8AEB\t\u8AEB \u8947
\u9730\t\u9730 \u7DDA
\u562F\t\u562F \u7B11
\u6548\t\u6548
\u53F7\t\u53F7
\u7B87\t\u7B87 \u904E
\u79A1\t\u79A1
\u6F3E\t\u6F3E \u5B95
\u656C\t\u6620 \u8ACD \u52C1
\u5F91\t\u5F91 \u8B49 \u5D9D
\u5BA5\t\u5BA5 \u5019 \u5E7C
\u6C81\t\u6C81
\u52D8\t\u52D8 \u95DE
\u8C54\t\u8C54 \U0002354A \u91C5
\u9677\t\u9677 \u9451 \u68B5
\u5C4B\t\u5C4B
\u6C83\t\u6C83 \u71ED
\u89BA\t\u89BA
\u8CEA\t\u8CEA \u8853 \u6ADB
\u7269\t\u7269 \u8FC4
\u6708\t\u6708 \u6C92
\u66F7\t\u66F7 \u672B
\u9EE0\t\u9EE0 \u938B
\u5C51\t\u5C51 \u859B
\u85E5\t\u85E5 \u9438
\u964C\t\u964C \u9EA5 \u6614
\u932B\t\u932B
\u8077\t\u8077 \u5FB7
\u7DDD\t\u7DDD
\u5408\t\u5408 \u76CD
\u8449\t\u8449 \u6017
\u6D3D\t\u6D3D \u72CE \u696D \u4E4F
'''.splitlines()]]))
assert len(set(miuk2bs.values())) == 106
assert set(miuk2bs.keys()) == set(miuklst)

box2sjep = dict(reduce(operator.add, [reduce(operator.add,
    [[(a[i], a[0])] for i in range(1, len(a))]) for a in [
    s.split() for s in u'''\
\u901A\t\u6771 \u51AC \u937E 
\u6C5F\t\u6C5F 
\u6B62\t\u652F \u8102 \u4E4B \u5FAE 
\u9047\t\u9B5A \u865E \u6A21 
\u87F9\t\u9F4A \u4F73 \u7686 \u7070 \u548D \u796D \u6CF0 \u592C \u5EE2 
\u81FB\t\u771E \u8AC4 \u81FB \u6587 \u6B23 \u9B42 \u75D5 
\u5C71\t\u5143 \u5BD2 \u6853 \u522A \u5C71 \u5148 \u4ED9 
\u6548\t\u856D \u5BB5 \u80B4 \u8C6A 
\u679C\t\u6B4C \u6208 
\u5047\t\u9EBB 
\u5B95\t\u967D \u5510 
\u6897\t\u5E9A \u8015 \u6E05 \u9752 
\u66FE\t\u84B8 \u767B 
\u6D41\t\u5C24 \u4FAF \u5E7D 
\u6DF1\t\u4FB5 
\u54B8\t\u8983 \u8AC7 \u9E7D \u6DFB \u54B8 \u929C \u56B4 \u51E1 
'''.splitlines()]]))
assert len(box2sjep) == 61

rom2py = {}

miuknotes = u'0123456789AB*.'

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
                try:
                    sjep = None
                    miuk = ar[1][2:].strip(miuknotes)
                    assert miuk in miuklst
                    sjep = miuk2sjep[miuk]
                    assert ar[8] == sjep
                    assert box2sjep[ar[5][0]] == sjep
                    if ar[22]:
                        assert miuk2bs[miuk] == ar[22]
                except:
                    print(sjep, miuk, file=sys.stderr)
                    raise
                assert ar[2] in sjenglst
                if ar[13]:
                    ckey = u''.join(map(ar.__getitem__, [8, 4, 3, 6, 5, 2]))
                    assert len(ckey) >= 6
                    if not ckey in rom2py:
                        rom2py[ckey] = ar[13]
                        assert gy2py(ckey) == ar[13] or ar[13] in ('hung4', 'shung4')
                    else:
                        assert rom2py[ckey] == ar[13]
                else:
                    print('No pinyin for ' + key, file=sys.stderr)
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
#    py2rom = {}
#    for k, v in rom2py.items():
#        py2rom.setdefault(v, set()).add(k)
#    for k in sorted(py2rom.keys()):
#        print(u'%s\t%s' % (k, u' '.join(sorted(py2rom[k]))), file=sys.stderr)
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

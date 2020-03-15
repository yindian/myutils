#!/usr/bin/env python
from __future__ import print_function
import sys
import struct
import io

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
                    elif o < 0x80:
                        continue
                    else:
                        assert not (0xDC00 <= o < 0xE000)
                        assert o < 0x110000
                        assert o >= 0x2E80
                    dd.setdefault(c, set()).add(key)
            except:
                print('Error processing %s %s' % (
                    ar[0],
                    ar[10],
                    ), file=sys.stderr)
                try:
                    print(usep.join(ar), file=sys.stderr)
                except:
                    raise
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
    no_apos = lambda s: s.replace("'", '')
    for c in sorted(dd.keys()):
        out.write((u'%s\t%s\n' % (
            c,
            u', '.join(sorted(dd[c], key=no_apos)),
            )).encode('utf-8'))
    try:
        sys.stdout.write(out.getvalue())
    except TypeError: # Python 3
        sys.stdout.buffer.write(out.getvalue())

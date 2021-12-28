#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import pprint
import re
import sys

extensions = 'old s3 s1 s2 china1 china2'.split()

code2hanzi = {}

def prn(*args, **kwargs):
    args = list(args)
    for i in range(len(args)):
        s = args[i]
        if type(s) != str:
            try:
                args[i] = s.encode('utf-8')
            except:
                pass
    print(*args, **kwargs)

def ext_idx(cls, s=None):
    try:
        return extensions.index(cls) + 1
    except ValueError:
        if s:
            prn(s, file=sys.stderr)
        return 0

try:
    unichr
except NameError:
    unichr = chr

tagpat = re.compile(r'<[^>]*>')

def check_unicode(s):
    if s.startswith('\uff5e') or s.startswith('*'):
        s = s[1:]
    try:
        assert s.startswith('U+')
    except:
        assert s.startswith('N/A')
    ar = s[2:].split(':')
    try:
        assert ord(ar[-1]) == int(ar[0], 16)
    except:
        if ar[-1].count('?') != len(ar[-1]):
            #prn(s, file=sys.stderr)
            pass
    if s.startswith('U+'):
        c = int(ar[0], 16)
        try:
            return unichr(c)
        except ValueError:
            assert c >= 0x10000
            c -= 0x10000
            return unichr(0xD800 + (c >> 10)) + unichr(0xDC00 + (c & 0x3FF))
    return tagpat.sub('', ':'.join(ar[1:]))

def parse_cccode(buf):
    lines = buf.decode('utf-8').splitlines()
    pre = False
    for s in lines:
        if not pre:
            pre = s.startswith('<pre>')
        else:
            pre = not s.startswith('</pre>')
            ar = s.split('\t', 1)
            if len(ar) != 2:
                continue
            try:
                n = int(ar[0])
                if ar[1].startswith('unassigned'):
                    assert ar[1] == 'unassigned'
                    code2hanzi[n] = None
                else:
                    t = ar[1].replace('&nbsp;', ' ').replace('<span ', '<span_').replace('<a ', '<a_')
                    br = t.split()
                    l = [None] * (len(extensions) + 1)
                    for t in br:
                        if t.startswith('<span_class="'):
                            cls = t[13:t.index('"', 13)]
                            l[ext_idx(cls)] = check_unicode(t[t.index('>') + 1:t.index('</span')])
                        else:
                            try:
                                assert l[0] is None
                            except:
                                #prn(s, '|', l[0], file=sys.stderr)
                                break
                            l[0] = check_unicode(t)
                    code2hanzi[n] = tuple(l)
            except:
                if ar[0] == '\u96fb\u78bc':
                    continue
                prn(s, file=sys.stderr)
                raise

def print_cccode(f=sys.stdout):
    assert len(code2hanzi) == 9999
    prn(','.join(['code', 'hkc'] + extensions), file=f)
    def none2empty(l):
        if l is None:
            l = [None] * (len(extensions) + 1)
        return [x or '' for x in l]
    for i in range(1, 10000):
        prn(','.join(['%04d' % (i,)] + none2empty(code2hanzi[i])), file=f)

if __name__ == '__main__':
    for c in sys.argv[1:]:
        with open(c, 'rb') as f:
            parse_cccode(f.read())
    print_cccode()
    #pprint.pprint(code2hanzi)

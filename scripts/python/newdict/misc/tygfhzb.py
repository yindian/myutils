#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os

def unalt(s):
    s = s.split(';')[0]
    p = s.find(':')
    if p >= 0:
        s = s[p+1:]
    assert s
    return s

assert __name__ == '__main__'

d = {}
dd = {}
fnb = {}
state = 0
last = None
for line in sys.stdin:
    try:
        if line.startswith('==附件'):
            state = int(line[8])
            last = None
        elif state == 0:
            if line.startswith(':'):
                p = line.index(' ')
                n = line[1:p]
                assert len(n) == 4
                s = line[p+1:].strip()
                p = s.find('{{')
                if p >= 0:
                    if s[p+2] == '!':
                        assert s[p+3] == '|'
                        q = s.index('|', p + 4)
                        t = s[q:]
                        s = s[p+4:q]
                        q = t.index('}}')
                        t = t[q+2:]
                    else:
                        t = s[p:]
                        s = s[:p]
                else:
                    t = ''
                if t:
                    assert t.startswith('{{fn|')
                    assert t.endswith('}}')
                    assert t[5:-2].isalnum()
                d[n] = [s, t, []]
                dd[s] = n
        elif state == 1:
            if line.startswith('|') and line[1] not in '-}':
                ar = line[1:].rstrip().split('||')
                assert len(ar) == 4
                if ar[0] != '"':
                    assert ar[0] in d
                    last = ar[0]
                else:
                    assert ar[1] == '"'
                    ar[1] = '〃'
                if ar[2] == '～':
                    ar[2] = '(～)'
                elif ar[2]:
                    st = d[last][2]
                    t = ar[2].decode('utf-8')
                    assert t.startswith(u'(') and t.endswith(u')')
                    t = t[1:-1]
                    p = 0
                    while p < len(t):
                        c = t[p]
                        if 0xD800 <= ord(c) < 0xDC00:
                            assert 0xDC00 <= ord(t[p+1]) < 0xE000
                            st.append(t[p:p+2].encode('utf-8'))
                            p += 2
                        elif c == u'<':
                            p = t.index(u'>', p + 1) + 1
                        elif c == u'{':
                            if t.startswith(u'{{fn', p):
                                p = t.index(u'}}', p + 4) + 2
                                continue
                            assert t.startswith(u'{{!|', p)
                            p += 4
                            q = t.index(u'|', p)
                            st.append(t[p:q].encode('utf-8'))
                            p = q + 1
                            q = t.index(u'}}', p)
                            st.append(t[p:q].encode('utf-8'))
                            p = q + 2
                        else:
                            assert not c.isspace()
                            st.append(c.encode('utf-8'))
                            p += 1
                    assert p == len(t)
                t = ar[3]
                st = []
                p = t.find('[[')
                while p >= 0:
                    assert t[p:p+7] == '[[File:'
                    q = t.index(']]', p + 7)
                    st.append(t[t.rindex('|', p + 7, q)+1:q])
                    t = t[:p] + st[-1] + t[q+2:]
                    p = t.find('[[')
                ar[3] = t
                if t:
                    p = t.find('<')
                    while p >= 0:
                        t = t[:p] + t[t.index('>', p + 1) + 1:]
                        p = t.find('<')
                    tp = tuple([s.decode('utf-8') for s in st])
                    st = d[last][2]
                    t = t.decode('utf-8')
                    assert t.startswith(u'[') and t.endswith(u']')
                    t = t[1:-1]
                    p = 0
                    while p < len(t):
                        c = t[p]
                        if t.startswith(tp, p):
                            for s in tp:
                                if t.startswith(s, p):
                                    s = s.strip()
                                    if s[0] in (u'(', u'（'):
                                        s = s[1:]
                                    if s[-1] in (u')', u'）'):
                                        s = s[:-1]
                                    assert s
                                    st.append(s.encode('utf-8'))
                                    p += len(s)
                                    break
                        elif 0xD800 <= ord(c) < 0xDC00:
                            assert 0xDC00 <= ord(t[p+1]) < 0xE000
                            st.append(t[p:p+2].encode('utf-8'))
                            p += 2
                        elif c == u'{':
                            if t.startswith(u'{{fn', p):
                                p = t.index(u'}}', p + 4) + 2
                                continue
                            assert t.startswith(u'{{!|', p)
                            p += 4
                            q = t.index(u'|', p)
                            st.append(t[p:q].encode('utf-8'))
                            p = q + 1
                            q = t.index(u'}}', p)
                            st.append(t[p:q].encode('utf-8'))
                            p = q + 2
                        elif c.isspace():
                            p += 1
                        else:
                            st.append(c.encode('utf-8'))
                            p += 1
                    assert p == len(t)
                t = d[last]
                t[1] += ''.join(['\n'] + ar[1:])
                if t[0] in st:
                    print >> sys.stderr, last, t[0], st
                    t[2] = [s for s in st if s != t[0]]
        elif state == 2:
            if line.startswith(':'):
                p = line.index(' ')
                n = line[1:p]
                assert len(n) == 4
                assert last
                d[n].append(last)
            elif line.startswith("'''"):
                last = line.rstrip().strip("'")
            elif line == '}-\n':
                state = 3
        elif state == 3:
            if line.startswith('=='):
                state = 4
                last = None
        else:
            if line.startswith('　'):
                assert last
            elif line.startswith('=='):
                continue
            elif line.startswith('{{'):
                break
            else:
                s = line
                if s.startswith('-{'):
                    p = s.index('}-', 2)
                    s = unalt(s[2:p])
                s = s.decode('utf-8')[0].encode('utf-8')
                if s in dd:
                    last = dd[s]
                elif s in '挼 㖞'.split():
                    continue
                else:
                    last = None
                    for n in d:
                        t = d[n][1]
                        if t.find(s) >= 0:
                            last = n
                            break
                    assert last
                d[last][1] += '\n'
            t = d[last]
            t[1] += '\n' + line.strip()
        if line.startswith('*'):
            assert line.startswith('*{{fnb|')
            p = line.index('}}', 7)
            s = line[7:p]
            assert s not in fnb
            t = line[p+2:].strip()
            p = t.find('{')
            while p >= 0:
                if t[p+1] == '{':
                    assert t[p+2] == '!'
                    assert t[p+3] == '|'
                    q = t.index('|', p + 4)
                    t = t[:p] + t[p+4:q] + t[t.index('}}', q) + 2:]
                else:
                    assert t[p-1] == '-'
                    q = t.index('}-', p + 1)
                    t = t[:p-1] + unalt(t[p+1:q]) + t[q+2:]
                p = t.find('{')
            fnb[s] = t
    except:
        sys.stderr.write(line)
        raise
level = '一级 二级 三级'.split()
dl = {}
kl = []
ds = {}
ks = []
for n in sorted(d.keys()):
    t = d[n]
    s = t[1]
    p = s.find('{')
    while p >= 0:
        if s[p:p+4] == '{{!|':
            q = s.index('|', p + 4)
            s = s[:p] + s[p+4:q] + s[s.index('}}', q) + 2:]
        elif s[p-1] == '-':
            q = s.index('}-')
            s = s[:p-1] + unalt(s[p+1:q]) + s[q+2:]
        else:
            try:
                assert s[p:p+5] == '{{fn|'
            except:
                print >> sys.stderr, s[p:p+5], p, s
                raise
            q = s.index('}}', p + 5)
            r = s.find('\n\n')
            if r < 0:
                s = s[:p] + s[q+2:] + '\n' + fnb[s[p+5:q]]
            else:
                assert q < r
                s = s[:p] + s[q+2:r] + '\n' + fnb[s[p+5:q]] + s[r:]
        p = s.find('{')
    p = s.find('<')
    while p >= 0:
        q = s.index('>', p + 1)
        s = s[:p] + s[q+1:]
        p = s.find('<')
    l = level[n > '6500' and 2 or (n > '3500' and 1 or 0)]
    s = '%s %s %s %s%s' % (
            l,
            t[-1],
            n,
            t[0],
            s)
    print '%s|%s\t%s' % (t[0], '|'.join([n] + t[2]), s.replace('\n', '\\n'))
    if l not in dl:
        dl[l] = []
        kl.append(l)
    dl[l].append(n)
    l = t[-1]
    if l not in ds:
        ds[l] = []
        ks.append(l)
    ds[l].append(n)
for l in kl:
    print '%s\t%s' % (l, ' '.join([d[n][0] for n in dl[l]]))
for l in ks:
    print '%s\t%s' % (l, ' '.join([d[n][0] for n in ds[l]]))

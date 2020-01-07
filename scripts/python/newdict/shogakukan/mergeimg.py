#!/usr/bin/env python
# -*- coding: utf-8 -*-
d = {}
with open('xxg2img.txt') as f:
    for line in f:
        a, b = line.split('\t')
        a = '|'.join(sorted(a.split('|')))
        br = [s[:s.index('<')] for s in b.split('<rref>') if s]
        try:
            assert not d.has_key(a)
        except:
            if d[a] == br:
                continue
            print a
            print d[a]
            print br
            raise
        d[a] = br
with open('xxg2.txt') as f:
    with open('xxg2i.txt', 'w') as g:
        for line in f:
            try:
                a, b = line.rstrip().split('\t')
                ar = a.split('|')
                assert len(ar) > 1
                try:
                    assert ar[1].replace(';', '').isalnum()
                except:
                    if ar[0].isalnum():
                        ar[:2] = ar[:2][::-1]
                    else:
                        raise
                assert b.find('<br') < 0
                br = b.split('<BR>')
                b = br[0].decode('utf-8')
                p = b.find(u'\uff08')
                if p > 0:
                    c = b[p-1]
                    while c == u'>':
                        p = b.rfind(u'<', 0, p-1)
                        assert p > 0
                        c = b[p-1]
                    try:
                        assert ar[0].decode('utf-8') == c
                    except:
                        try:
                            p = ar.index(c.encode('utf-8'))
                            ar[0], ar[p] = ar[p], ar[0]
                        except:
                            if ar[0] == '澳洲黑' and ar[2] == '鸡':
                                ar[2] = '澳洲黑鸡'
                cr = [ar[0]] + ar[2:]
                c = '|'.join(sorted(cr))
                while c:
                    if c in d:
                        s = br[-1]
                        p = s.find('<img')
                        while p >= 0:
                            assert s.startswith('<img src="')
                            assert s.endswith('">')
                            del br[-1]
                            s = br[-1]
                            p = s.find('<img')
                        br.extend(['<img src="%s">' % (s,) for s in d.pop(c)])
                        break
                    del cr[-1]
                    c = '|'.join(sorted(cr))
                print >> g, '%s\t%s' % ('|'.join(ar), '<BR>'.join(br))
            except:
                print line
                raise
print '\n'.join(d.keys())

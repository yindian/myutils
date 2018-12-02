#!/usr/bin/env python
import sys
import glob
import operator

enc = 'mbcs'

def tosec(s):
    assert s.endswith(u'\u79d2')
    p = len(s) - 2
    while p >= 0 and s[p].isdigit():
        p -= 1
    r = int(s[p+1:-1])
    if p > 0:
        assert s[p] == u'\u5206'
        r += int(s[:p]) * 60
    return r

def tostr(t):
    s = '%d' % (t % 60,)
    if t >= 60:
        t /= 60
        s = '%02d:%s' % (t % 60, s)
        if t >= 60:
            s = '%d:%s' % (t / 60, s)
    return s

def tomin(t):
    a, b = divmod(t, 60)
    return a + cmp(b, 0)

assert __name__ == '__main__'

if len(sys.argv) > 1:
    flist = map(open, reduce(operator.add, map(glob.glob, sys.argv[1:]), []))
else:
    flist = [sys.stdin]
d = {}
d2 = {}
t = {}
for f in flist:
    for line in f:
        ar = line.decode(enc).split('\t')
        if len(ar) > 4 and ar[0][0].isdigit():
            if ar[2] == u'\u4e3b\u53eb':
                num = ar[3]
                d[num] = d.get(num, 0) + tosec(ar[4])
                d2[num] = d2.get(num, 0) + tomin(tosec(ar[4]))
                t[num] = t.get(num, 0) + 1
    f.close()
ar = d.items()
ar.sort(key=lambda x: x[1], reverse=True)
print 'Phone No.\tMinutes\tDur(s)\tCount\tTotal\tAvg. Dur'
for num, dur in ar:
    print '%s\t%d\t%d\t%d\t%s\t%s' % (num, d2[num], dur, t[num], tostr(dur), tostr(dur / t[num]))
dur = sum(d.values())
tim = sum(t.values())
print '%s\t%d\t%d\t%d\t%s\t%s' % ('Total No.', sum(d2.values()), dur, tim, tostr(dur), tostr(dur / tim))

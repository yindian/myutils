#!/usr/bin/env python
import sys
import glob
import operator
import quopri

enc = None
enclist = 'mbcs utf-8 cp936'.split()

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

def parse_fn(s):
    p = s.index(':')
    ar = s[:p].split(';')
    s = s[p+1:]
    assert ar[0] == 'FN'
    d = dict([x.upper().split('=') for x in ar[1:]])
    if d.get('ENCODING') == 'QUOTED-PRINTABLE':
        s = quopri.decodestring(s)
    s = s.decode(d.get('CHARSET', 'UTF-8'))
    return s

assert __name__ == '__main__'

if len(sys.argv) > 1:
    flist = map(open, reduce(operator.add, map(glob.glob, sys.argv[1:]), []))
else:
    flist = [sys.stdin]
nd = {}
d = {}
d2 = {}
t = {}
b = {}
for f in flist:
    enc = None
    state = 0
    for line in f:
        if enc is None:
            for enc in enclist:
                try:
                    line.decode(enc)
                    break
                except:
                    pass
        ar = line.decode(enc).split('\t')
        if len(ar) > 4 and ar[0][0].isdigit():
            ar = [s.rstrip() for s in ar]
            if ar[2].endswith(u'\u4e3b\u53eb'):
                num = ar[3]
                if len(num) < 8:
                    num = num.ljust(8)
                d[num] = d.get(num, 0) + tosec(ar[4])
                d2[num] = d2.get(num, 0) + tomin(tosec(ar[4]))
                t[num] = t.get(num, 0) + 1
                b[num] = b.get(num, 0.) + float(ar[7])
        elif len(ar) == 1:
            if state == 0:
                if line.startswith('BEGIN:VCARD'):
                    state = 1
                    fn = []
                    tel = []
            elif line.startswith('END:VCARD'):
                try:
                    fn = ','.join([parse_fn(x) for x in fn])
                except:
                    print fn
                    raise
                for c in tel:
                    if c in nd:
                        nd[c] = '%s,%s' % (nd[c], fn)
                    else:
                        nd[c] = fn
                state = 0
            elif line.startswith('TEL'):
                tel.append(line[line.index(':')+1:].rstrip().replace('-', ''))
                state = 1
            elif line.startswith('FN') and line[2] in ';:':
                fn.append(line.rstrip().rstrip('='))
                state = 2
            elif state == 2:
                if line.find(':') < 0:
                    fn[-1] += line.strip()
                else:
                    state = 1
    f.close()
ar = d.items()
ar.sort(key=lambda x: x[1], reverse=True)
if nd:
    print 'Phone No.\tMinutes\tDur(s)\tCount\tTotal\tAvg.Dur\tBill\tContact'
    for num, dur in ar:
        print '%s\t%d\t%d\t%d\t%s\t%s\t%.2f\t%s' % (num, d2[num], dur, t[num], tostr(dur), tostr(dur / t[num]), b[num], nd.get(num, '') or nd.get('+86'+num, ''))
else:
    print 'Phone No.\tMinutes\tDur(s)\tCount\tTotal\tAvg.Dur\tBill'
    for num, dur in ar:
        print '%s\t%d\t%d\t%d\t%s\t%s\t%.2f' % (num, d2[num], dur, t[num], tostr(dur), tostr(dur / t[num]), b[num])
dur = sum(d.values())
tim = sum(t.values())
if t:
    print '%s\t%d\t%d\t%d\t%s\t%s\t%.2f' % ('Total No.', sum(d2.values()), dur, tim, tostr(dur), tostr(dur / tim), sum(b.values()))

#!/usr/bin/env python
import sys, os

assert __name__ == '__main__'
if len(sys.argv) < 2:
    print('Usage: %s tabfile.txt' % (os.path.basename(sys.argv[0]),))
    sys.exit(0)

SP = ' '
NL = '<BR>\\n'
NLNL = NL + NL
REF = lambda x: '<A href="bword://%s">%s</A>' % (x, x)

lst = []
dic = {}
syn = {}

with open(sys.argv[1]) as f:
    for line in f:
        try:
            line = line.rstrip('\n')
            k, v = line.split('\t', 1)
            ar = k.split('|')
            h = ar[0]
            if h not in dic:
                lst.append(h)
                dic[h] = []
            dic[h].append(v)
            for s in ar[1:]:
                if s not in syn or h not in syn[s]:
                    syn.setdefault(s, []).append(h)
        except:
            print(line)
            if ar[0] in dic:
                print(dic[ar[0]])
            raise

for s in sorted(syn.keys()):
    if s not in dic:
        lst.append(s)
        dic[s] = []
    dic[s].append(SP.join([REF(h) for h in syn[s]]))

for k in lst:
    print('%s\t%s' % (k, NLNL.join(dic[k])))

#!/usr/bin/env python
import sys
import os.path
assert __name__ == '__main__'
path = sys.argv[2]
with open(sys.argv[1]) as f:
    for line in f:
        ar = line.split('<rref>')
        for i in xrange(1, len(ar)):
            p = ar[i].index('</rref>')
            s = ar[i][:p]
            if os.path.exists(os.path.join(path, s)):
                pass
            elif s.endswith('jpg') and os.path.exists(
                    os.path.join(path, s[:-3] + 'png')):
                ar[i] = s[:-3] + 'png' + ar[i][p:]
            elif s.endswith('avi') and os.path.exists(
                    os.path.join(path, s + '.jpg')):
                ar[i] = s + '.jpg' + ar[i][p:]
            elif s.endswith('wav'):
                pass
            else:
                print >> sys.stderr, s
        sys.stdout.write('<rref>'.join(ar))

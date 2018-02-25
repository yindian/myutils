#!/usr/bin/env python
import sys
import string
assert __name__ == '__main__'
f = open(sys.argv[1])
g = open(sys.argv[2])
hexset = set(string.hexdigits)
d = {}
for line in f:
    p = line.index(' ')
    digest = line[:p]
    assert set(digest) <= hexset
    q = p + 1
    while q < len(line) and line[q] == ' ':
        q += 1
    d[digest] = line[q:-1]
for line in g:
    p = line.index(' ')
    digest = line[:p]
    assert set(digest) <= hexset
    q = p + 1
    while q < len(line) and line[q] == ' ':
        q += 1
    if d.has_key(digest):
        print '# %s' % (digest,)
        print 'ln -s "%s" "%s"' % (d[digest], line[q:-1])
f.close()
g.close()

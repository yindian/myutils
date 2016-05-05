#!/usr/bin/env python
import numpy as np
from scipy.spatial.distance import pdist, squareform
import scipy.cluster.hierarchy as hier
import re
import sys
import pdb

assert __name__ == '__main__'

pat = re.compile(r'^Comparing (\S+) with (\S+)\.')
pat2 = re.compile(r'^(../)?([^/]+)([0-9]+[ab]?)/.*\3-(.*)\..*')
f = open('dist')
a = b = None
labels = []
array = []
data = []
for line in f:
    m = pat.match(line)
    if m:
        a, b = [pat2.sub(r'\2\3/\4', x) for x in (m.group(1), m.group(2))]
    else:
        if a not in labels:
            labels.append(a)
        if b not in labels:
            labels.append(b)
        try:
            d = float(line.split()[-1])
        except:
            pdb.set_trace()
            raise
        array.append(d)
        data.append(((labels.index(a), labels.index(b)), d))
f.close()
matrix = [[0] * len(labels) for i in xrange(len(labels))]
for (i, j), d in data:
    matrix[i][j] = d
    matrix[j][i] = d
array = np.array(array)
square = squareform(array)
matrix = np.array(matrix)
assert np.array_equal(square, matrix)

#np.set_printoptions(threshold=np.nan, linewidth=10000)
#print square

clusters = hier.linkage(array, 'average')
idx = hier.fcluster(clusters, 0.6, 'distance')
assert len(idx) == len(labels)
idx = idx.tolist()
#print idx

s = set(range(len(labels)))
while s:
    k = s.pop()
    c = idx[k]
    t = []
    for i in xrange(len(labels)):
        if idx[i] == c:
            t.append(i)
            idx[i] = 0
            if i != k:
                s.remove(i)
    for i in t:
        print labels[i],
    print

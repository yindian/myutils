#!/usr/bin/env python
import sys
import struct
import socket
import math
from bisect import *
import traceback
import pdb
assert __name__ == '__main__'
try:
    max_ips = int(sys.argv[1], 0)
    i = 2
except:
    max_ips = 100
    i = 1
try:
    min_mask = int(sys.argv[i], 0)
    i += 1
except:
    min_mask = 13
try:
    f = open(sys.argv[i])
except:
    f = sys.stdin
d = {}
for line in f:
    line = line.rstrip();
    if not line:
        continue
    try:
        ip, cnt = line.split()
        cnt = int(cnt)
        ip = socket.inet_aton(ip)
        ip = struct.unpack('!L', ip)[0]
    except:
        print >> sys.stderr, line
        traceback.print_exc()
        continue
    try:
        d[ip] += cnt
    except KeyError:
        d[ip] = cnt
l = d.keys()
for k in d.iterkeys():
    d[k] = (32, d[k], 0.) # mask, count, 1 - coverage
while len(d) > max_ips:
    ar = d.keys()
    ar.sort()
    br = []
    t = {}
    sm = set()
    for i in xrange(len(ar)):
        ip = ar[i]
        mask = d[ip][0]
        assert mask
        mask -= 1
        ip &= (1 << 32) - (1 << (32 - mask))
        ret = None
        while mask in sm:
            if t.has_key((ip, mask)):
                ret = t[(ip, mask)]
                break
            ip &= (1 << 32) - (1 << (32 - mask))
            mask -= 1
        if not ret:
            ip = ar[i]
            mask, count, penalty = d[ip]
            mask -= 1
            unmask = 1 << (32 - mask)
            ip &= (1 << 32) - unmask
            penalty /= 2.
            if ip < ar[i]:
                ip_next = ar[i]
                j = i - 1
                while j >= 0:
                    try:
                        ip2 = ar[j]
                    except IndexError:
                        break
                    if ip2 & ((1 << 32) - unmask) != ip:
                        break
                    mask2, count2, penalty2 = d[ip2]
                    count += count2
                    penalty += (ip_next - ip2 - (1 << (32 - mask2))) * 1. / unmask
                    penalty += penalty2 / (1 << (mask2 - mask))
                    ip_next = ip2
                    j -= 1
                penalty += (ip_next - ip) * 1. / unmask
                k = j + 1
            else:
                k = i
            ip_next = ar[i] + (unmask >> 1)
            j = i + 1
            while True:
                try:
                    ip2 = ar[j]
                except IndexError:
                    break
                if ip2 & ((1 << 32) - unmask) != ip:
                    break
                mask2, count2, penalty2 = d[ip2]
                count += count2
                penalty += (ip2 - ip_next) * 1. / unmask
                penalty += penalty2 / (1 << (mask2 - mask))
                ip_next = ip2 + (1 << (32 - mask2))
                j += 1
            penalty += (ip + unmask - ip_next) * 1. / unmask
            ret = t[(ip, mask)] = (k, j - k, ip, mask, count, penalty, penalty / (j - k))
            if mask not in sm:
                sm.add(mask)
                while mask < 32:
                    mask += 1
                    sm.add(mask)
        br.append(ret)
    min_i = -1
    min_score = math.exp(32)
    score_field = -1
    for i in xrange(len(ar)):
        if br[i][1] < 2:
            continue
        score = br[i][score_field]
        if score < min_score:
            min_i = i
            min_score = score
    if min_i < 0:
        max_count = max([x[-3] for x in br])
        max_count = math.log(max_count)
        for i in xrange(len(ar)):
            score = br[i][-2] / math.log(br[i][-3] + 0.1) * max_count * (math.exp(32) / math.exp(br[i][-4])) ** 0.5
            if score < min_score:
                min_i = i
                min_score = score
    assert min_i >= 0
    min_br = br[min_i]
    #print >> sys.stdout, min_i, len(d), min_score, '%s/%d' % (socket.inet_ntoa(struct.pack('!L', min_br[2])), min_br[3]), min_br, ' '.join(['%s/%d' % (socket.inet_ntoa(struct.pack('!L', ar[i])), d[ar[i]][0]) for i in xrange(min_br[0], min_br[0] + min_br[1])])
    if min_br[3] < min_mask:
        break
    for i in xrange(min_br[0], min_br[0] + min_br[1]):
        del d[ar[i]]
    d[min_br[2]] = min_br[3:6]

if True:
    l.sort()
    to_del = []
    for k in d.keys():
        ip = k
        mask, count, penalty = d[ip]
        unmask = 1 << (32 - mask)
        ips = set()
        for i in xrange(bisect_left(l, ip), len(l)):
            if l[i] & ((1 << 32) - unmask) == ip:
                ips.add(l[i])
            else:
                break
        assert len(ips)
        while mask < 32:
            mask += 1
            unmask = 1 << (32 - mask)
            ip2 = ip + unmask
            ok1 = ok2 = True
            for x in ips:
                if x & ((1 << 32) - unmask) != ip:
                    ok1 = False
                if x & ((1 << 32) - unmask) != ip2:
                    ok2 = False
                if not (ok1 or ok2):
                    break
            if ok1:
                pass
            elif ok2:
                ip = ip2
            else:
                mask -= 1
                break
        if ip == k and mask != d[k][0]:
            d[ip] = mask, count, 1. - len(ips) * 1. / (1 << (32 - mask)), ips
        elif ip != k:
            assert not d.has_key(ip)
            to_del.append(k)
            d[ip] = mask, count, 1. - len(ips) * 1. / (1 << (32 - mask)), ips
        else:
            assert abs(penalty - 1. + len(ips) * 1. / (1 << (32 - mask))) < 1e-5
            d[ip] = mask, count, penalty, ips
    for k in to_del:
        del d[k]
else:
    for k in d.keys():
        ip = k
        mask, count, penalty = d[ip]
        d[ip] = mask, count, penalty, set()

ar = [('%s/%d' % (socket.inet_ntoa(struct.pack('!L', k)), v[0]), v[1], v[2], ' '.join([socket.inet_ntoa(struct.pack('!L', x)) for x in v[3]])) for k, v in d.iteritems()]
ar.sort(key=lambda x: x[1], reverse=True)
for x in ar:
    print '\t'.join(map(str, x))

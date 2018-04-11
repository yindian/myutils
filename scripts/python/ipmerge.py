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
white_list = set()
try:
    while True:
        ip = socket.inet_aton(sys.argv[i])
        ip = struct.unpack('!L', ip)[0]
        white_list.add(ip)
        i += 1
except:
    pass
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
        try:
            cnt = int(cnt)
        except:
            cnt = float(cnt)
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
for ip in white_list:
    try:
        assert not d.has_key(ip)
    except:
        print >> sys.stderr, ip
        raise
l = d.keys()
l.sort()
r = set([(0, 0)])
rm = 0

def shrink_subnet(ips, ip, mask):
    if True:
        while mask < 32:
            mask += 1
            unmask = 1 << (32 - mask)
            ip2 = ip + unmask
            unmask = (1 << 32) - unmask
            ok1 = ok2 = True
            for x in ips:
                if x & unmask != ip:
                    ok1 = False
                if x & unmask != ip2:
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
    return ip, mask, len(ips) * 1. / (1 << (32 - mask))

while len(r) < max_ips or rm < min_mask or white_list:
    to_del = []
    s = set([x[0] for x in r if x[1] == rm])
    assert s
    chosen_ip = None
    chosen_ip1 = chosen_mask1 = None
    chosen_ip2 = chosen_mask2 = None
    max_score = -1.
    if white_list:
        s.clear()
        rm = 32
        for w in white_list:
            found = False
            for ip, mask in r:
                unmask = 1 << (32 - mask)
                unmask = (1 << 32) - unmask
                if w & unmask == ip:
                    if mask < rm:
                        s.clear()
                        rm = mask
                        s.add(ip)
                    elif mask == rm:
                        s.add(ip)
                    found = True
                    break
            if not found:
                to_del.append(w)
        for w in to_del:
            white_list.remove(w)
        if not white_list and not s:
            rm = 32
            for ip, mask in r:
                if mask < rm:
                    s.clear()
                    rm = mask
                    s.add(ip)
                elif mask == rm:
                    s.add(ip)
            assert s
    for ip in s:
        mask = rm
        unmask = 1 << (32 - mask)
        unmask = (1 << 32) - unmask
        ips = set()
        for i in xrange(bisect_left(l, ip), len(l)):
            if l[i] & unmask == ip:
                ips.add(l[i])
            else:
                break
        assert len(ips)
        coverage = len(ips) * 1. / (1 << (32 - mask))
        mask += 1
        unmask = 1 << (32 - mask)
        ip2 = ip + unmask
        unmask = (1 << 32) - unmask
        ips1 = set()
        ips2 = set()
        for k in ips:
            if k & unmask == ip:
                ips1.add(k)
            else:
                assert k & unmask == ip2
                ips2.add(k)
        ip1, mask1, coverage1 = shrink_subnet(ips1, ip, mask)
        ip2, mask2, coverage2 = shrink_subnet(ips2, ip2, mask)
        score = coverage1 + coverage2 - coverage - coverage
        if score > max_score:
            max_score = score
            chosen_ip = ip
            chosen_ip1, chosen_mask1 = ip1, mask1
            chosen_ip2, chosen_mask2 = ip2, mask2
    if chosen_ip is None:
        break
    r.remove((chosen_ip, rm))
    r.add((chosen_ip1, chosen_mask1))
    r.add((chosen_ip2, chosen_mask2))
    rm = 32
    for ip, mask in r:
        if mask < rm:
            rm = mask
    if rm == 32:
        break
t = {}
for ip, mask in r:
    unmask = 1 << (32 - mask)
    unmask = (1 << 32) - unmask
    ips = set()
    for i in xrange(bisect_left(l, ip), len(l)):
        if l[i] & unmask == ip:
            ips.add(l[i])
        else:
            break
    assert len(ips)
    coverage = len(ips) * 1. / (1 << (32 - mask))
    t[ip] = mask, sum([d[k] for k in ips]), 1. - coverage, ips
d = t

ar = [('%s/%d' % (socket.inet_ntoa(struct.pack('!L', k)), v[0]), v[1], v[2], ' '.join([socket.inet_ntoa(struct.pack('!L', x)) for x in v[3]])) for k, v in d.iteritems()]
ar.sort(key=lambda x: x[1], reverse=True)
for x in ar:
    print '\t'.join(map(str, x))

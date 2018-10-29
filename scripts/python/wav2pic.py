#!/usr/bin/env python
import sys, os
import struct
import wave
import math
from PIL import Image, ImageDraw
from cStringIO import StringIO

def load_samples(fname):
    w = wave.open(fname)
    assert w.getsampwidth() == 2
    count = w.getnchannels() * w.getnframes()
    buf = w.readframes(count)
    r = w.getframerate()
    w.close()
    ar = struct.unpack('%dh' % (count,), buf)
    if w.getnchannels() == 2:
        ar = ar[0::2]
    assert len(ar) == w.getnframes()
    return ar, r

def store_samples(fname, ar, rate=44100):
    w = wave.open(fname, 'wb')
    w.setnchannels(1)
    w.setframerate(rate)
    w.setsampwidth(2)
    buf = struct.pack('%dh' % (len(ar),), *ar)
    w.writeframes(buf)
    w.close()

def find_phase(ar, period):
    br = [x * x for x in ar]
    k, s = 0, sum(br[0::period])
    for i in xrange(1, period):
        t = sum(br[i::period])
        if t < s:
            k, s = i, t
    return k

def main(fname_wav, freq=80, fname_pic=None):
    freq = int(freq)
    ar, rate = load_samples(fname_wav)
    period = int(round(rate * 1. / freq))
    phase = find_phase(ar, period)
    br = []
    mm = max(map(abs, ar))
    func = sum
    #func = max
    if not phase:
        pass
    elif phase * 2 <= period:
        br.append(func(map(abs, ar[:phase])) * period / phase)
    else:
        br.append(func(map(abs, ar[:phase] + ar[phase * 2 - period:phase])))
    for i in xrange(phase, len(ar), period):
        br.append(func(map(abs, ar[i:i + period])))
    if phase:
        del br[-1]
    m = max(br)
    step = 16
    amp = 160
    #step, amp = [x * 2 for x in (step, amp)]
    upscale = 8
    step, amp = [x * upscale for x in (step, amp)]
    ar = [int(round(1. * x * amp / m)) for x in br]
    img = Image.new('L', (len(ar) * step, amp * 2), 0)
    draw = ImageDraw.Draw(img)
    for i in xrange(len(ar)):
        w = min(ar[i] * 2, step / 2)
        x = int(math.ceil((step - w) / 2.))
        draw.ellipse((step * i + x, amp - ar[i], step * (i + 1) - x, amp + ar[i]), 255)
    img = img.resize([x / upscale for x in img.size], Image.BILINEAR)
    mask = img
    img = Image.new('RGBA', img.size, (222, 210, 115, 0))
    img.putalpha(mask)
    sf = StringIO()
    img.save(sf, 'PNG')
    if fname_pic:
        with open(fname_pic, 'wb') as f:
            f.write(sf.getvalue())
    else:
        sys.stdout.write(sf.getvalue())
    print >> sys.stderr, ar
    root, ext = os.path.splitext(fname_wav)
    br = []
    for x in ar:
        peak = x * m * math.pi / (period * amp * 2.)
        #peak = x * mm / amp
        cr = []
        for i in xrange(period):
            cr.append(peak * math.sin(math.pi * 2. * i / period))
        dr = map(int, map(round, cr))
        er = map(int, cr)
        assert func(map(abs, er)) <= x * m / amp
        diff = func(map(abs, dr)) - x * m / amp
        if func == sum:
            if diff > 0:
                while diff > 0:
                    mn = 1.
                    k = -1
                    for i in xrange(period):
                        if dr[i] != er[i]:
                            assert abs(dr[i] - er[i]) == 1
                            d = abs(cr[i] - (dr[i] + er[i]) / 2.)
                            if d < mn:
                                mn = d
                                k = i
                    assert k >= 0
                    if dr[k] > 0:
                        assert dr[k] == er[k] + 1
                    else:
                        assert dr[k] == er[k] - 1
                    dr[k] = er[k]
                    diff -= 1
            elif diff < 0:
                while diff < 0:
                    mx = 0.
                    k = -1
                    for i in xrange(period):
                        if dr[i] == er[i]:
                            d = abs(cr[i] - dr[i])
                            if d > mx:
                                mx = d
                                k = i
                    assert k >= 0
                    assert cr[k] != 0.
                    if cr[k] > 0:
                        dr[k] += 1
                    else:
                        dr[k] -= 1
                    diff += 1
            assert func(map(abs, dr)) == x * m / amp
        br.extend(dr)
    store_samples(root + '-xform' + ext, br, rate)

if __name__ == '__main__':
    main(*sys.argv[1:])

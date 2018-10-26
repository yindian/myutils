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
    func = sum
    #func = max
    #def func(l):
    #    l.sort()
    #    return l[len(l) / 2]
    if phase * 2 <= period:
        br.append(func(map(abs, ar[:phase])) * period / phase)
    else:
        br.append(func(map(abs, ar[:phase] + ar[phase * 2 - period:phase])))
    for i in xrange(phase, len(ar), period):
        br.append(func(map(abs, ar[i:i + period])))
    del br[-1]
    m = max(br)
    step = 16
    amp = 160
    #step, amp = [x * 2 for x in (step, amp)]
    upscale = 8
    step, amp = [x * upscale for x in (step, amp)]
    ar = [x * amp / m for x in br]
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

if __name__ == '__main__':
    main(*sys.argv[1:])

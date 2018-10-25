#!/usr/bin/env python
import sys, os
import struct
import wave
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
    for i in xrange(phase, len(ar), period):
        br.append(sum(map(abs, ar[i:i + period])))
    del br[-1]
    m = max(br)
    step = 10
    amp = 100
    ar = [x * amp / m for x in br]
    img = Image.new('L', (len(ar) * step, amp * 2), 255)
    draw = ImageDraw.Draw(img)
    for i in xrange(len(ar)):
        w = min(ar[i], step / 2)
        x = (step - w) / 2
        draw.rectangle((step * i + x, amp - ar[i], step * (i + 1) - x, amp + ar[i]), 0)
    sf = StringIO()
    img.save(sf, 'PNG')
    if fname_pic:
        with open(fname_pic, 'wb') as f:
            f.write(sf.getvalue())
    else:
        sys.stdout.write(sf.getvalue())

if __name__ == '__main__':
    main(*sys.argv[1:])

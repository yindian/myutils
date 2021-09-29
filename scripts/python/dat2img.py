#!/usr/bin/env python3
import io
import os.path

jpg0 = 0xFF
jpg1 = 0xD8
gif0 = 0x47
gif1 = 0x49
png0 = 0x89
png1 = 0x50

def Dat2Image(datpath, imgpath=None, out=None):
    with io.open(datpath, 'rb') as f:
        b = f.read()
    if len(b) < 2:
        raise Exception("image size error")
    b = bytearray(b)
    j0 = b[0] ^ jpg0
    j1 = b[1] ^ jpg1
    g0 = b[0] ^ gif0
    g1 = b[1] ^ gif1
    p0 = b[0] ^ png0
    p1 = b[1] ^ png1
    if j0 == j1:
        v = j0
        ext = "jpg"
    elif g0 == g1:
        v = g0
        ext = "gif"
    elif p0 == p1:
        v = p0
        ext = "png"
    else:
        raise Exception("unknown image format")
    for i in range(len(b)):
        b[i] ^= v
    if not imgpath:
        imgpath = '%s.%s' % (os.path.splitext(datpath)[0], ext)
    else:
        imgpath = '%s.%s' % (os.path.splitext(imgpath)[0], ext)
    if out:
        out.write('%s => %s\n' % (datpath, imgpath))
    with io.open(imgpath, 'wb') as f:
        f.write(b)

if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 2:
        sys.stdout.write('Usage: %s datpath imgpath [datpath imgpath ...]\n' % (
            os.path.basename(sys.argv[0]),))
        sys.exit(0)
    p = 1
    while p < len(sys.argv):
        Dat2Image(sys.argv[p], sys.argv[p + 1], sys.stdout)
        p += 2

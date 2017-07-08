#!/usr/bin/env python
import sys
import os, tempfile, shutil, glob
from Crypto.Cipher import DES
from zipfile import ZipFile
import traceback

assert __name__ == '__main__'

key = '\xfe\xb8\xf5m\xecJ\xff\xc6'
cipher = DES.new(key)
unpad = lambda s: s[0:-ord(s[-1])]

if len(sys.argv) < 2:
    print 'Usage: %s zipfile' % (sys.argv[0],)
    sys.exit(0)

for fname in sys.argv[1:]:
    try:
        z = ZipFile(fname, 'r')
        d = tempfile.mkdtemp()
        z.extractall(d)
        z.close()
    except:
        traceback.print_exc()
        continue
    for book in glob.glob(os.path.join(d, '*.epub')):
        name = os.path.basename(book)
        z = ZipFile(book, 'r')
        dd = os.path.join(d, name[:-5])
        os.mkdir(dd)
        z.extractall(dd)
        z.close()
        f = open(os.path.join(dd, 'OEBPS/content.opf'))
        for line in f:
            if line.find('application/xhtml') > 0 and line.find('<opf:item') >= 0:
                p = line.index('href="')
                chapter = line[p+6:line.index('"', p+6)]
                g = open(os.path.join(dd, 'OEBPS', chapter))
                buf = g.read()
                g.close()
                buf = unpad(cipher.decrypt(buf))
                g = open(os.path.join(dd, 'OEBPS', chapter), 'w')
                g.write(buf)
                g.close()
        f.close()
        z = ZipFile(name, 'w')
        for root, dirs, files in os.walk(dd):
            for s in files:
                z.write(os.path.join(root, s), os.path.relpath(os.path.join(root, s), dd))
        z.close()
    shutil.rmtree(d)

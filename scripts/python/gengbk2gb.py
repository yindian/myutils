#!/usr/bin/env python
# -*- coding: gb2312 -*-
template = """\
#include <stdio.h>
#include <malloc.h>

typedef unsigned short int wchar_gbk;

typedef struct {
    wchar_gbk fan;
    wchar_gbk jian;
    char *    jian_alt;
} charmap_pair;

#define NUM_CHARS %(charmaplen)d
charmap_pair charmap[];

wchar_gbk gbk_f2j(wchar_gbk in, char **alt)
{
    int low=0,high=NUM_CHARS-1,mid;
    wchar_gbk wc_gb_mid, out = in;

    *alt = NULL;
    while (low<=high)
    {
        mid = (low+high) >> 1;
        wc_gb_mid = charmap[mid].fan;
        if (in == wc_gb_mid)
        {
            out = charmap[mid].jian;
            *alt = charmap[mid].jian_alt;
            break;
        }
        else
        {
            if (in < wc_gb_mid)
            {
                high = mid - 1;
            }
            else
            {
                low = mid + 1;
            }
        }
    }

    return out;
}
int main(int argc, char** argv)
{
    int ch;
    wchar_gbk wc_gbk, wc_gb;
    char * s;
#define OBUFSIZE 4096
    char * stdobuf;

    stdobuf = malloc(OBUFSIZE);
    setvbuf(stdout, stdobuf, stdobuf != NULL ? _IOFBF : _IONBF, OBUFSIZE);

    ch = getc(stdin);
    while ( ch != EOF )
    {
        if (ch > 0x80)  /* 对GBK字符 */
        {
            wc_gbk = (ch << 8) + getc(stdin);
            ch = getc(stdin);

            wc_gb = gbk_f2j(wc_gbk, &s);
            if (s)
                fputs(s, stdout);
            else
            {
                putchar(wc_gb >> 8);
                putchar(wc_gb & 0xFF);
            }
        }
        else /* 对ASCII字符,直接输出 */
        {
            putchar(ch);
            if (ch == '\\n')
                fflush(stdout);
            ch = getc(stdin);
        }
    }
    fflush(stdout);
    return 0;
}

charmap_pair charmap[] = {
    %(charmap)s
};
"""

def uni2gbk(ch):
	s = ch.encode('gb18030')
	return int(s.encode('hex'), 16)

def uni2gb(ch):
	s = ch.encode('gb2312')
	return int(s.encode('hex'), 16)

assert __name__ == '__main__'

import sys, os

if len(sys.argv) < 2:
	print "Usage: %s fullset.txt" % (os.path.basename(sys.argv[0]),)
	sys.exit(0)

mapping = {}
f = open(sys.argv[1], 'r')
lineno = 0
try:
	for line in f:
		lineno += 1
		line = line.rstrip().decode('utf-8')
		if not line or line[0] == u'#':
			pass
		elif line.find(u'#') > 0:
			ar = filter(None, line.split(u'#'))
			assert len(ar) >= 2
			if mapping.has_key(ar[0]):
				print >> sys.stderr, 'Duplicate mapping from %s to %s, %s' % (ar[0], mapping[ar[0]], ar[1])
				sys.exit(1)
			mapping[ar[0]] = ar[1]
		else:
			assert len(line) == 1
			mapping[line] = None
except:
	print >> sys.stderr, 'Error on line', lineno
	raise
f.close()

for k in mapping.keys():
	if not mapping[k]:
		continue
	v = mapping[k]
	while mapping.has_key(v) and mapping[v]:
		v = mapping[v]
	mapping[k] = v

charmap = []
for k in mapping.keys():
	if not mapping[k]:
		continue
	if len(mapping[k]) == 1:
		wc_gbk, wc_gb = uni2gbk(k), uni2gb(mapping[k])
		if wc_gbk != wc_gb:
			charmap.append('{0x%04x, 0x%04x, NULL},' % (
				wc_gbk,
				wc_gb))
	else:
		wc_gbk = uni2gbk(k)
		assert len(mapping[k]) > 0
		charmap.append('{0x%04x, 0x%04x, "%s"},' % (
			wc_gbk, wc_gbk,
			mapping[k].encode('gb2312')))
charmap.sort()

sys.stdout.write(template % {
	'charmap': '\n    '.join(charmap),
	'charmaplen': len(charmap),
	})

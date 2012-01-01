/*
   Copyright 2010, Kunihiko Sadakane, all rights reserved.

   This software may be used freely for any purpose.
   No warranty is given regarding the quality of this software.
   */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "csa.h"
#include "cst.h"
#ifdef printf
#undef printf
#endif

int main(int argc, char *argv[])
{
    i64 i,n;
    CSA SA;
    char *key;

    if (argc < 4) {
        fprintf(stderr, "syntax: suftest file key [-c]\n");
        return -1;
    }

    csa_read(&SA,2, argv+1);
    n = SA.n;

    key = argv[3];
    {
#define BUFLEN 256
#define MAXRESULT 500
        char buf[256];
        char *p, *q;
        i64 keylen;
        i64 l,r;
        i64 s,t,j,k;
        keylen = strlen(key);
        s = SA.search(key,keylen,&SA,&l,&r);
        if (s == keylen) {
            printf("%d\n", r-l+1);
            if (argc >= 5 && strcmp(argv[4], "-c") == 0)
                return 0;
            if (r-l+1 > MAXRESULT) r = l+MAXRESULT-1;

            for (i=l; i<=r; i++) {
                j = SA.lookup(&SA,i);
                s = max(j-20,0);
                do {
                    k = min(s+19, j-1);
                    SA.text(buf,&SA,s,k);
                    buf[k-s+1] = '\0';
                    if ((p=strrchr(buf, '\n'))) break;
                    s = max(s-20,0);
                } while (s > max(0, j-BUFLEN));
                t = min(j+20+keylen-1,SA.n-1);
                k = j+keylen;
                do {
                    SA.text(buf,&SA,k,t);
                    buf[t-k+1] = '\0';
                    if ((q=strchr(buf, '\n'))) break;
                    k = t + 1;
                    t = min(t+20,SA.n-1);
                } while (t < min(SA.n-1, j+BUFLEN));
                if (q) q += k - j - keylen;
                SA.text(buf,&SA,s,j-1);
                if (!p) putchar('.'),putchar('.'),putchar('.');
                for (k=p-buf+1; k<j-s; k++) putchar(buf[k]);
                for (k=0; k<keylen; k++) putchar(key[k]);
                SA.text(buf,&SA,j+keylen,t);
                if (!q) {
                    for (k=0; k<t-j-keylen+1; k++) putchar(buf[k]);
                    putchar('.'),putchar('.'),putchar('.');
                } else {
                    for (k=0; k<q-buf; k++) putchar(buf[k]);
                }
                putchar('\n');
            }
        } else {
            return s;
        }
    }

    return 0;
}

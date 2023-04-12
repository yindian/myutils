#ifdef USE_HASH
#include "khash.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#ifndef _MSC_VER
#include <stdint.h>
#else
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef unsigned __int64 uint64_t;
#endif
#include <string.h>
#ifdef _MSC_VER
#define PRIu64 "I64u"
#else
#include <inttypes.h>
#endif
#ifdef _WIN32
#include <fcntl.h>
#endif
#if defined(__GNUC__) && __GNUC__ >= 7
#define FALL_THROUGH __attribute__((fallthrough))
#else
#define FALL_THROUGH /* fall through */
#endif
#define USE_BJOERN
#ifdef USE_BJOERN
// Copyright (c) 2008-2010 Bjoern Hoehrmann <bjoern@hoehrmann.de>
// See http://bjoern.hoehrmann.de/utf-8/decoder/dfa/ for details.

#define UTF8_ACCEPT 0
#define UTF8_REJECT 12

static const uint8_t utf8d[] = {
  // The first part of the table maps bytes to character classes that
  // to reduce the size of the transition table and create bitmasks.
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,  9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,
   7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,  7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
   8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,  2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
  10,3,3,3,3,3,3,3,3,3,3,3,3,4,3,3, 11,6,6,6,5,8,8,8,8,8,8,8,8,8,8,8,

  // The second part is a transition table that maps a combination
  // of a state of the automaton and a character class to a state.
   0,12,24,36,60,96,84,12,12,12,48,72, 12,12,12,12,12,12,12,12,12,12,12,12,
  12, 0,12,12,12,12,12, 0,12, 0,12,12, 12,24,12,12,12,12,12,24,12,24,12,12,
  12,12,12,12,12,12,12,24,12,12,12,12, 12,24,12,12,12,12,12,12,12,24,12,12,
  12,12,12,12,12,12,12,36,12,36,12,12, 12,36,12,12,12,12,12,36,12,36,12,12,
  12,36,12,12,12,12,12,12,12,12,12,12, 
};

static uint32_t
decode(uint32_t* state, uint32_t* codep, uint32_t byte) {
  uint32_t type = utf8d[byte];

  *codep = (*state != UTF8_ACCEPT) ?
    (byte & 0x3fu) | (*codep << 6) :
    (0xff >> type) & (byte);

  *state = utf8d[256 + *state + type];
  return *state;
}
#else
#ifdef USE_ASM
extern int utf8_decode_asm(const unsigned char **inbufp, size_t inbufsz, unsigned int **outbufp, size_t outbufsz);
#else
#include "utf8.h"
#endif
#endif
#ifdef USE_HASH
KHASH_MAP_INIT_INT(cnt, uint64_t)
#else
#define UNICODE_POINTS 0x110000
static uint64_t cnt[UNICODE_POINTS] = {0};
#endif
#define BUFLEN 0x8000
#ifdef BUFLEN
#ifdef STATIC_BUF
static unsigned char buf[BUFLEN];
#endif
#ifndef USE_BJOERN
#ifdef USE_ASM
static uint32_t outbuf[BUFLEN];
#endif
#endif
#endif
int main()
{
#ifdef USE_HASH
    int ret;
    khiter_t k;
    khash_t(cnt) *h = kh_init(cnt);
#endif
    int ch;
    uint32_t b /* state */, c /* code point */;
#ifdef BUFLEN
#ifndef STATIC_BUF
    unsigned char *buf;
#endif
    size_t l;
#endif
    uint64_t n;
#ifdef DEBUG_TOTAL
    uint64_t total, totalU;
    total = totalU = 0;
#endif
#if 0
    setvbuf(stdin, NULL, _IOFBF, 1024 * 4);
#endif
#ifdef _WIN32
    _setmode(_fileno( stdin ), _O_BINARY);
#define getchar _getchar_nolock
#else
    if (!freopen(NULL, "rb", stdin))
    {
        perror("freopen");
        return 1;
    }
#define getchar getchar_unlocked
#endif
    b = c = 0;
#ifndef BUFLEN
    while ((ch = getchar()) != EOF)
#else
#ifndef STATIC_BUF
    buf = (unsigned char *) malloc(BUFLEN);
#endif
    for (l = fread(buf, 1, BUFLEN, stdin); l;
         l += fread(buf + l, 1, BUFLEN - l, stdin))
#endif
    {
#ifdef BUFLEN
        unsigned char *p = buf;
        unsigned char *end = buf + l;
        while (end > p && (end[-1]>>6) == 2) /* stop at ascii or leading byte */
        {
            --end;
        }
        if (end > p && (end[-1]>>6) == 3) /* leading byte */
        {
            --end;
        }
        if (end == p) /* unlikely */
        {
            ++end;
        }
#ifdef DEBUG_TOTAL
        total += l;
#endif
#else
#ifdef DEBUG_TOTAL
        ++total;
#endif
#endif
#ifdef USE_BJOERN
#ifdef BUFLEN
        for (; p < end; ++p)
        {
        ch = *p;
#endif
#ifdef CARE_REJECT
        switch (decode(&b, &c, ch))
#else
        if (decode(&b, &c, ch) == UTF8_ACCEPT)
#endif
#else
#ifndef BUFLEN
#error "BUFLEN Missing"
#endif
        (void) b;
#ifdef USE_ASM
        (void) ch;
        {
        uint32_t *outp = outbuf;
        uint32_t *q;
        utf8_decode_asm(&p, end - p, &outp, sizeof(outbuf));
        for (q = outbuf; q < outp; ++q)
        {
        c = *q;
#else
        for (p = buf + l; ((p - buf) & 3); ++p)
        {
            *p = '\0';
        }
        for (p = buf; p < end; )
        {
        p = utf8_decode(p, &c, &ch); /* ch: E */
        if (!ch)
#endif
#endif
        {
#ifdef USE_BJOERN
#ifdef CARE_REJECT
            case UTF8_REJECT:
                c = 0xFFFF;
                b = 0;
                FALL_THROUGH;
            case UTF8_ACCEPT:
#endif
#endif
#ifdef USE_HASH
                k = kh_get(cnt, h, c);
                if (k != kh_end(h))
                {
                    kh_value(h, k)++;
                }
                else
                {
                    k = kh_put(cnt, h, c, &ret);
                    kh_value(h, k) = 1;
                }
#else
                ++cnt[c];
#endif
#ifdef USE_BJOERN
#ifdef CARE_REJECT
                break;
            default:
                break;
#endif
#endif
        }
#ifdef BUFLEN
#ifndef USE_BJOERN
#ifdef USE_ASM
        }
#endif
#endif
#ifdef USE_BJOERN
#ifndef CARE_REJECT
        else if (b == UTF8_REJECT)
        {
            b = 0;
        }
#endif
        }
#else
#ifdef USE_ASM
        }
#else
        }
#endif
#endif
        l = buf + l - p;
        memmove(buf, p, l);
#ifdef DEBUG_TOTAL
        total -= l;
#endif
#endif
    }
#ifdef BUFLEN
#ifndef STATIC_BUF
    free(buf);
#endif
#endif
#ifdef USE_HASH
    kh_foreach(h, c, n, printf("%04X\t%" PRIu64 "\n", c, n));
#ifdef DEBUG_TOTAL
    kh_foreach(h, c, n, totalU += n);
#endif
    kh_destroy(cnt, h);
#else
    for (c = 0; c < UNICODE_POINTS; ++c)
    {
        if ((n = cnt[c]))
        {
            printf("%04X\t%" PRIu64 "\n", c, n);
#ifdef DEBUG_TOTAL
            totalU += n;
#endif
        }
    }
#endif
#ifdef DEBUG_TOTAL
    fprintf(stderr, "Total %" PRIu64 " bytes, %" PRIu64 " characters\n", total, totalU);
#endif
    return 0;
}

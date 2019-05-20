#include "khash.h"
#include <stdio.h>
#include <stdint.h>
#ifdef _MSC_VER
#define PRIu64 "I64"
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
#if 1
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
#endif
KHASH_MAP_INIT_INT(cnt, uint64_t)
int main()
{
    int ret;
    khiter_t k;
    khash_t(cnt) *h = kh_init(cnt);
    int ch;
    uint32_t b /* state */, c /* code point */;
    uint64_t n;
    setvbuf(stdin, NULL, _IOFBF, 1024 * 4);
#ifdef _WIN32
    _setmode(_fileno( stdin ), _O_BINARY);
#define getchar _getchar_nolock
#else
#define getchar getchar_unlocked
#endif
    b = c = 0;
    while ((ch = getchar()) != EOF)
    {
        switch (decode(&b, &c, ch))
        {
            case UTF8_REJECT:
                c = 0xFFFF;
                FALL_THROUGH;
            case UTF8_ACCEPT:
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
                break;
            default:
                break;
        }
    }
    kh_foreach(h, c, n, printf("%04X\t%" PRIu64 "\n", c, n));
    kh_destroy(cnt, h);
    return 0;
}

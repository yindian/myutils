#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
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
#define BUFLEN 0x8000
#ifdef BUFLEN
#ifdef STATIC_BUF
static unsigned char buf[BUFLEN];
#endif
#endif
/* line terminator flags */
#define F_LF		1
#define F_VT		2
#define F_FF		4
#define F_CR		8
#define F_CRLF		16
#define F_NEL		32
static const char *line_term_str[] = {
	"LF",
	"VT",
	"FF",
	"CR",
	"CRLF",
	"NEL",
	NULL
};
static uint32_t add_sat(uint32_t a, uint32_t b)
{
	uint32_t c = a + b;
	if (c < a)
	{
		c = (uint32_t) -1;
	}
	return c;
}
int main()
{
    int ch, lastCh;
#ifdef BUFLEN
#ifndef STATIC_BUF
    unsigned char *buf;
#endif
    size_t l;
#endif
	uint32_t flags, nCR;
    uint64_t nChar, nLine, nWidth, nMaxWidth, nPosMax, nLineMax;
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
	lastCh = EOF;
	flags = nCR = 0;
    nChar = nLine = nWidth = nMaxWidth = nPosMax = nLineMax = 0;
#ifndef BUFLEN
    while ((ch = getchar()) != EOF)
#else
#ifndef STATIC_BUF
    buf = (unsigned char *) malloc(BUFLEN);
#endif
    for (l = fread(buf, 1, BUFLEN, stdin); l;
         l = fread(buf, 1, BUFLEN, stdin))
#endif
    {
#ifdef BUFLEN
        unsigned char *p = buf;
        unsigned char *end = buf + l;
        for (; p < end; ++p)
        {
        ch = *p;
#endif
		++nChar;
		++nWidth;
		switch (ch)
		{
			case '\n': /* LF */
				if (lastCh == '\r')
				{
					flags |= F_CRLF;
					--nCR;
				}
				else
				{
					++nLine;
					flags |= F_LF;
				}
				if (nWidth > nMaxWidth)
				{
					nMaxWidth = nWidth;
					nPosMax = nChar;
					nLineMax = nLine;
				}
				nWidth = 0;
				break;
			case '\r': /* CR */
				++nLine;
				nCR = add_sat(nCR, 1);
				break;
			case 0x0B: /* VT */
				++nLine;
				flags |= F_VT;
				break;
			case 0x0C: /* FF */
				++nLine;
				flags |= F_FF;
				break;
#if 0
			case 0x85: /* NEL */
				if (lastCh == 0xC2) /* UTF-8 leading byte */
				{
					++nLine;
					flags |= F_NEL;
				}
				break;
#endif
			default:
				break;
		}
		lastCh = ch;
#ifdef BUFLEN
		}
#endif
    }
#ifdef BUFLEN
#ifndef STATIC_BUF
    free(buf);
#endif
#endif
	if (nCR)
	{
		flags |= F_CR;
	}
	if (nWidth)
	{
		++nLine;
		if (nWidth > nMaxWidth)
		{
			nMaxWidth = nWidth;
			nPosMax = nChar;
			nLineMax = nLine;
		}
	}
	printf("Char count:\t%" PRIu64 "\n", nChar);
	printf("Line count:\t%" PRIu64 "\n", nLine);
	printf("Max L width:\t%" PRIu64 "\t@%" PRIu64 "\t#%" PRIu64 "\n", nMaxWidth, nPosMax - nMaxWidth, nLineMax);
	printf("Avg L width:\t%" PRIu64 "\n", nLine ? nChar / nLine : 0);
	printf("Line term:");
	{
		const char **p;
		for (p = line_term_str; *p; ++p)
		{
			if ((flags & 1))
			{
				printf("\t%s", *p);
			}
			flags >>= 1;
		}
	}
	printf("\n");
    return 0;
}

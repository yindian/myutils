#include "posix_port.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <malloc.h>
#include <string.h>
static char *code2utf(wchar_t code, char buf[])
{
	char *q;
	q = buf;
	if (code <= 0x0000007f)
		*q++ = code;
	else if (code <= 0x000007ff)
	{
		*q++ = 0xc0 | (code >> 6);
		*q++ = 0x80 | (code & 0x3f);
	}
	else if (code <= 0x0000ffff)
	{
		*q++ = 0xe0 | (code >> 12);
		*q++ = 0x80 | ((code >> 6) & 0x3f) ;
		*q++ = 0x80 | (code & 0x3f);
	}
	else if (code <= 0x001fffff)
	{
		*q++ = 0xf0 | (code >> 18);
		*q++ = 0x80 | ((code >> 12) & 0x3f) ;
		*q++ = 0x80 | ((code >> 6) & 0x3f) ;
		*q++ = 0x80 | (code & 0x3f);
	}
	else if (code <= 0x03ffffff)
	{
		*q++ = 0xf8 | (code >> 24);
		*q++ = 0x80 | ((code >> 18) & 0x3f) ;
		*q++ = 0x80 | ((code >> 12) & 0x3f) ;
		*q++ = 0x80 | ((code >> 6) & 0x3f) ;
		*q++ = 0x80 | (code & 0x3f);
	}
	else if (code <= 0x7fffffff)
	{
		*q++ = 0xfc | (code >> 30);
		*q++ = 0x80 | ((code >> 24) & 0x3f) ;
		*q++ = 0x80 | ((code >> 18) & 0x3f) ;
		*q++ = 0x80 | ((code >> 12) & 0x3f) ;
		*q++ = 0x80 | ((code >> 6) & 0x3f) ;
		*q++ = 0x80 | (code & 0x3f);
	}
	else
		assert(code <= 0x7fffffff);
	*q = '\0';
	return buf;
}

static char *wc2utf8(const wchar_t *wp)
{
    size_t wlen = wcslen(wp);
    char buf[6];
    char *res = (char *) malloc(wlen * 4);
    char *p = res;
    for (; *wp; wp++)
    {
        code2utf(*wp, buf);
        strcpy(p, buf);
        p += strlen(buf);
    }
    return res;
}

int _wmkdir(const wchar_t *wpath)
{
    char *path = wc2utf8(wpath);
    //fprintf(stderr, "_wmkdir: %s\n", path);
    int ret = mkdir(path, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
    free(path);
    return ret;
}

FILE *_wfopen(const wchar_t *wpath, const wchar_t *wmode)
{
    char *path = wc2utf8(wpath);
    char *mode = wc2utf8(wmode);
    //fprintf(stderr, "_wfopen: %s, %s\n", path, mode);
    FILE *ret = fopen(path, mode);
    free(path);
    free(mode);
    return ret;
}

#define UI32BE2LE(_x) ((((unsigned long)(_x) & 0xFF000000) >> 24) | (((unsigned long)(_x) & 0xFF0000) >> 8) | (((unsigned long)(_x) & 0xFF00) << 8) | (((unsigned long)(_x) & 0x00FF) << 24))

wchar_t *_fgetws(wchar_t *ws, int n, FILE *stream)
{
    int i;
    unsigned char buf[2];
    size_t len;
    for (i = 0; i < n - 1; i++)
    {
        len = fread(buf, 1, 2, stream);
        if (len == 2)
        {
            ws[i] = buf[0] | (buf[1] << 8);
        }
        else
        {
            if (i == 0)
                return NULL;
            break;
        }
    }
    ws[i] = 0;
    return ws;
}

int getch()
{
    return getchar();
}

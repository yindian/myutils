#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#ifdef _MSC_VER
#define PRIu64 "I64"
#else
#include <inttypes.h>
#endif
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#if defined(__GNUC__) && __GNUC__ >= 7
#define FALL_THROUGH __attribute__((fallthrough))
#else
#define FALL_THROUGH /* fall through */
#endif

#define BUFLEN 1024

static int isname(int c)
{
	return c == '.' || c == '-' || c == '_' || c == ':' ||
		(c >= '0' && c <= '9') ||
		(c >= 'A' && c <= 'Z') ||
		(c >= 'a' && c <= 'z');
}

static int iswhite(int c)
{
	return c == ' ' || c == '\r' || c == '\n' || c == '\t';
}

int main(int argc, char *argv[])
{
    uint64_t nLine;
    unsigned nCol;
    int ch;
    int wrap, match, output;
    int bufpos, pathpos, docpos;
    int lastpathpos;
    char *buf, *path, *doc;
    const char *errmsg;
    wrap = match = output = 0;
    bufpos = pathpos = docpos = 0;
    lastpathpos = 0;
    buf = (char *) malloc(BUFLEN);
    assert(buf);
    path = (char *) malloc(BUFLEN);
    assert(path);
    path[0] = '\0';
    doc = (char *) malloc(BUFLEN);
    assert(doc);
#define CHECK_LIMIT(_cond) do \
    { \
        if (!(_cond)) \
        { \
            errmsg = "buffer limit exceeded"; \
            goto parse_end; \
        } \
    } while (0)
#ifdef _WIN32
    _setmode(_fileno( stdin ), _O_BINARY);
#define getchar _getchar_nolock
#else
#define getchar getchar_unlocked
#endif
    nLine = 1;
    nCol = 0;
#define ON_NEW_LINE
#define READ_CHAR_ROUTINE(_c) do \
    { \
        (_c) = getchar(); \
        if ((_c) == EOF) goto parse_end; \
        if ((_c) == '\n') {++nLine; nCol = 0; ON_NEW_LINE;} \
        else ++nCol; \
    } while (0)

parse_text:
    errmsg = NULL;
    bufpos = 0;
    READ_CHAR_ROUTINE(ch);
    while (ch != '<')
    {
        READ_CHAR_ROUTINE(ch);
    }
#if 0
    goto parse_element;

parse_element:
#endif
	errmsg = "syntax error in element";
    READ_CHAR_ROUTINE(ch);
	if (ch == '/') goto parse_closing_element;
	if (ch == '!') goto parse_comment;
	if (ch == '?') goto parse_processing_instruction;
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (isname(ch)) goto parse_element_name;
    goto parse_end;

parse_comment:
	errmsg = "end of data in comment";
    READ_CHAR_ROUTINE(ch);
	if (ch == '[') goto parse_cdata;
	if (ch == 'D')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch != 'O') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'C') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'T') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'Y') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'P') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'E') break;
            goto parse_declaration;
        } while (0);
        errmsg = "syntax errmsg in declaration (<!D not followed by OCTYPE)";
        goto parse_end;
    }
	if (ch == 'E')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch != 'N') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'T') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'I') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'T') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != 'Y') break;
            goto parse_declaration;
        } while (0);
        errmsg = "syntax errmsg in declaration (<!E not followed by NTITY)";
        goto parse_end;
    }
	if (ch != '-')
    {
        errmsg = "syntax error in comment (<! not followed by --)";
        goto parse_end;
    }
    READ_CHAR_ROUTINE(ch);
	if (ch != '-')
    {
        errmsg = "syntax error in comment (<!- not followed by -)";
        goto parse_end;
    }
    for (;;)
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch != '-') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != '-') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != '>') break;
            goto parse_text;
        } while (0);
	}
#if 0
    goto parse_end;
#endif

parse_declaration:
	errmsg = "end of data in declaration";
    do
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch == '"')
            {
                do
                {
                    READ_CHAR_ROUTINE(ch);
                } while (ch != '"');
            }
            else if (ch == '\'')
            {
                do
                {
                    READ_CHAR_ROUTINE(ch);
                } while (ch != '\'');
            }
        } while (0);
    } while (ch != '>');
	goto parse_text;

parse_cdata:
    errmsg = "syntax error in CDATA section";
    do
    {
        READ_CHAR_ROUTINE(ch);
        if (ch != 'C') break;
        READ_CHAR_ROUTINE(ch);
        if (ch != 'D') break;
        READ_CHAR_ROUTINE(ch);
        if (ch != 'A') break;
        READ_CHAR_ROUTINE(ch);
        if (ch != 'T') break;
        READ_CHAR_ROUTINE(ch);
        if (ch != 'A') break;
        READ_CHAR_ROUTINE(ch);
        if (ch != '[') break;
        goto parse_cdata_next;
    } while (0);
    goto parse_end;
parse_cdata_next:
	errmsg = "end of data in CDATA section";
    for (;;)
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch != ']') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != ']') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != '>') break;
            goto parse_text;
        } while (0);
	}
#if 0
    goto parse_end;
#endif

parse_processing_instruction:
	errmsg = "end of data in processing instruction";
    for (;;)
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (ch != '?') break;
            READ_CHAR_ROUTINE(ch);
            if (ch != '>') break;
            goto parse_text;
        } while (0);
	}
#if 0
    goto parse_end;
#endif

parse_closing_element:
    errmsg = "syntax error in closing element";
    READ_CHAR_ROUTINE(ch);
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
    buf[0] = '/';
    bufpos = 1;
	while (isname(ch))
    {
        buf[bufpos++] = ch;
        READ_CHAR_ROUTINE(ch);
    }
    CHECK_LIMIT(bufpos < BUFLEN);
    buf[bufpos] = '\0';
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (ch != '>') goto parse_end;
    if (lastpathpos)
    {
        char *p = strrchr(path, '/');
        assert(p);
        lastpathpos = p - path;
    }
    if (strcmp(buf, path + lastpathpos))
    {
        errmsg = "closing element mismatch";
        goto parse_end;
    }
    pathpos = lastpathpos;
    path[pathpos] = '\0';
	goto parse_text;

parse_element_name:
	errmsg = "syntax error in element name";
    lastpathpos = pathpos;
    path[pathpos++] = '/';
	while (isname(ch))
    {
        path[pathpos++] = ch;
        READ_CHAR_ROUTINE(ch);
    }
    CHECK_LIMIT(pathpos < BUFLEN);
    path[pathpos] = '\0';
    if (!match)
    {
        puts(path);
    }
#if 0
    goto parse_attributes;
#endif

parse_attributes:
	errmsg = "syntax error in attributes";
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (isname(ch)) goto parse_attribute_name;
	if (ch == '>') goto parse_text;
    if (ch == '/')
    {
        READ_CHAR_ROUTINE(ch);
        if (ch != '>') goto parse_end;
        pathpos = lastpathpos;
        path[pathpos] = '\0';
        goto parse_text;
    }
    goto parse_end;

parse_attribute_name:
	errmsg = "syntax error in attribute name";
	while (isname(ch))
    {
        READ_CHAR_ROUTINE(ch);
    }
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (ch == '=') goto parse_attribute_value;
    goto parse_end;

parse_attribute_value:
	errmsg = "end of data in attribute value";
    READ_CHAR_ROUTINE(ch);
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
    if (ch == '"')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
        } while (ch != '"');
    }
    else if (ch == '\'')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
        } while (ch != '\'');
    }
    else
    {
		errmsg = "missing quote character";
        goto parse_end;
    }
    READ_CHAR_ROUTINE(ch);
    goto parse_attributes;

parse_end:
    if (errmsg)
    {
        fprintf(stderr, "%s on line %" PRIu64 " col %u\n", errmsg, nLine, nCol);
        fprintf(stderr, "path: %s pos %d last %d\n", path,pathpos, lastpathpos);
        fprintf(stderr, "buf: %*s, doc: %*s\n", bufpos, buf, docpos, doc);
    }
    free(buf);
    free(path);
    free(doc);
    if (errmsg)
    {
        return 1;
    }
    printf("%" PRIu64 "\n", nLine);
    return 0;
}

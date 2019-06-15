#include <stdio.h>
#include <stdlib.h>
#ifndef _MSC_VER
#include <stdint.h>
#else
typedef unsigned __int64 uint64_t;
#endif
#include <string.h>
#include <assert.h>
#ifdef _MSC_VER
#define PRIu64 "I64u"
#define strtoull _strtoui64
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

#define NO_HASH

#define DJB2_EMPTY_STR_HASH         (5381UL)
#define DJB2_HASH_UPDATE(_h, _c)    ((_h) = ((((_h) << 5) + (_h)) + (_c)))

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
    uint64_t nLine2Show;
    uint64_t nLine;
    unsigned nCol;
    int i;
    int ch;
    int cbegin;
    int wrap, output;
    int help;
    int bufpos, pathpos, docpos;
    int lastpathpos;
    int top;
#ifndef NO_HASH
    unsigned long hash, pathhash;
    unsigned long *stackpathhash;
#endif
    int *stackpathpos;
    char *buf, *path, *doc;
    const char *errmsg;
    const char *show, *match, *pattern;
#ifndef NO_HASH
    unsigned long showhash;
#endif
    wrap = output = 0;
    bufpos = pathpos = docpos = 0;
    lastpathpos = 0;
    top = 0;
#ifndef NO_HASH
    pathhash = DJB2_EMPTY_STR_HASH;
    showhash = DJB2_EMPTY_STR_HASH;
#endif
    help = 0;
    show = match = pattern = NULL;
    nLine2Show = 0;
    for (i = 1; i < argc; i++)
    {
        if (argv[i][0] == '-')
        {
            switch (argv[i][1])
            {
                case 's':
                    if (show)
                    {
                        help = 1;
                        break;
                    }
                    show = &argv[i][2];
                    break;
                case 'm':
                    if (match)
                    {
                        help = 1;
                        break;
                    }
                    match = &argv[i][2];
                    break;
                default:
                    help = 1;
                    break;
            }
            if ((show && show[0] != '/') || (match && match[0] != '/'))
            {
                help = 1;
            }
            if (help)
            {
                break;
            }
        }
        else if (pattern)
        {
            help = 1;
            break;
        }
        else
        {
            pattern = argv[i];
        }
    }
    if (help)
    {
    }
    else
    if (pattern)
    {
        if (!match)
        {
            char *p;
            nLine2Show = strtoull(pattern, &p, 0);
            help = (p && *p != '\0');
            pattern = NULL;
        }
        else if (!show)
        {
            show = match;
        }
    }
    else if (match)
    {
        match = NULL;
    }
    if (help)
    {
        printf("Usage: %s [-s/path/to/show] [-m/path/to/match] [pattern]\n",
               argv[0]);
        printf("Note: XML data is fed through stdin in a streaming manner\n");
        printf("Pattern is matched in character data under path of -m\n");
        printf("If no path of -m specified, pattern is treated as line num\n");
        printf("On pattern / line match, element under path of -s is shown\n");
        printf("If no pattern is specified, show all elements under -s path\n");
        printf("Without arguments, show element structure of the document\n");
        printf("Output in PYX notation, enhanced with / - path, # - note\n");
        return 0;
    }
#ifndef NO_HASH
    if (show)
    {
        unsigned char *p;
        for (p = (unsigned char *) show; *p; ++p)
        {
            DJB2_HASH_UPDATE(showhash, *p);
        }
    }
#endif
#ifdef NO_SHOW
    (void) output;
#endif
#ifdef NO_MATCH
    (void) wrap;
    (void) match;
#endif
    buf = (char *) malloc(BUFLEN);
    assert(buf);
    path = (char *) malloc(BUFLEN);
    assert(path);
    path[0] = '\0';
    doc = (char *) malloc(BUFLEN);
    assert(doc);
    stackpathpos = (int *) malloc(BUFLEN);
    assert(stackpathpos);
#ifndef NO_HASH
    stackpathhash = (unsigned long *) malloc(BUFLEN);
    assert(stackpathhash);
#endif
    puts("(LBXG");
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
    cbegin = 1;
#undef ON_NEW_LINE
#ifndef NO_SHOW
#define ON_NEW_LINE if(output){if(!cbegin)putchar('\n');puts("-\\n");} cbegin=1
#else
#define ON_NEW_LINE cbegin = 1
#endif
    READ_CHAR_ROUTINE(ch);
#ifndef NO_SHOW
    if (output)
    {
    while (ch != '<')
    {
        {
            int out = 0;
            if (cbegin)
            {
                if (!iswhite(ch))
                {
                    cbegin = 0;
                    putchar('-');
                    out = 1;
                }
            }
            else
            {
                out = 1;
            }
            if (out)
            {
                if (ch == '&')
                {
#undef ON_NEW_LINE
#define ON_NEW_LINE
                    do
                    {
                        int code = -1;
                        READ_CHAR_ROUTINE(ch);
                        if (ch == '#')
                        {
                            char s[16] = {0};
                            char *p;
                            int i = 0;
                            do
                            {
                                READ_CHAR_ROUTINE(ch);
                                s[i++] = ch;
                            } while (ch != ';' && i != sizeof(s));
                            if (i == sizeof(s) || i < 2) break;
                            if (s[0] == 'x')
                            {
                                code = (int) strtoul(s + 1, &p, 16);
                            }
                            else
                            {
                                code = (int) strtoul(s, &p, 10);
                            }
                            if (*p != ';') break;
                            if (code < 0) break;
                        }
                        else if (ch == 'l')
                        {
                            READ_CHAR_ROUTINE(ch);
                            if (ch != 't') break;
                            READ_CHAR_ROUTINE(ch);
                            if (ch != ';') break;
                            code = '<';
                        }
                        else if (ch == 'g')
                        {
                            READ_CHAR_ROUTINE(ch);
                            if (ch != 't') break;
                            READ_CHAR_ROUTINE(ch);
                            if (ch != ';') break;
                            code = '>';
                        }
                        else if (ch == 'a')
                        {
                            READ_CHAR_ROUTINE(ch);
                            if (ch == 'm')
                            {
                                READ_CHAR_ROUTINE(ch);
                                if (ch != 'p') break;
                                READ_CHAR_ROUTINE(ch);
                                if (ch != ';') break;
                                code = '&';
                            }
                            else if (ch == 'p')
                            {
                                READ_CHAR_ROUTINE(ch);
                                if (ch != 'o') break;
                                READ_CHAR_ROUTINE(ch);
                                if (ch != 's') break;
                                READ_CHAR_ROUTINE(ch);
                                if (ch != ';') break;
                                code = '\'';
                            }
                            else
                            {
                                break;
                            }
                        }
                        else if (ch == 'q')
                        {
                            READ_CHAR_ROUTINE(ch);
                            if (ch != 'u') break;
                            READ_CHAR_ROUTINE(ch);
                            if (ch != 'o') break;
                            READ_CHAR_ROUTINE(ch);
                            if (ch != 't') break;
                            READ_CHAR_ROUTINE(ch);
                            if (ch != ';') break;
                            code = '"';
                        }
                        else
                        {
                            break;
                        }
                        if (code < 0x80)
                        {
                            putchar(code);
                        }
                        else if (code < 0x800)
                        {
                            putchar(0xC0 | (code >> 6));
                            putchar(0x80 | (code & 0x3F));
                        }
                        else if (code < 0x10000)
                        {
                            putchar(0xE0 | (code >> 12));
                            putchar(0x80 | ((code >> 6) & 0x3F));
                            putchar(0x80 | (code & 0x3F));
                        }
                        else if (code < 0x110000)
                        {
                            putchar(0xF0 | (code >> 18));
                            putchar(0x80 | ((code >> 12) & 0x3F));
                            putchar(0x80 | ((code >> 6) & 0x3F));
                            putchar(0x80 | (code & 0x3F));
                        }
                        else
                        {
                            break;
                        }
                        goto parse_entity_next;
                    } while (0);
                    errmsg = "unrecognized entity";
                    goto parse_end;
#undef ON_NEW_LINE
#define ON_NEW_LINE if(output){if(!cbegin)putchar('\n');puts("-\\n");} cbegin=1
                }
                else
                {
                    putchar(ch);
                }
            }
        }
parse_entity_next:
        READ_CHAR_ROUTINE(ch);
    }
    if (!cbegin)
    {
        putchar('\n');
    }
    }
    else
#endif
    {
        while (ch != '<')
        {
            READ_CHAR_ROUTINE(ch);
        }
    }
#undef ON_NEW_LINE
#define ON_NEW_LINE
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
#undef ON_NEW_LINE
#define ON_NEW_LINE cbegin = 1
    for (;;)
    {
        char s[4] = {0};
        int lastcbegin = cbegin;
        do
        {
            READ_CHAR_ROUTINE(ch);
            s[0] = ch;
            if (ch != ']') break;
            READ_CHAR_ROUTINE(ch);
            s[1] = ch;
            if (ch != ']') break;
            READ_CHAR_ROUTINE(ch);
            s[2] = ch;
            if (ch != '>') break;
#ifndef NO_SHOW
            if (output && !cbegin)
            {
                putchar('\n');
            }
#endif
            goto parse_text;
        } while (0);
#ifndef NO_SHOW
        if (output)
        {
            char *p;
            cbegin = lastcbegin;
            for (p = s; (ch = *p); ++p)
            {
                if (ch == '\n')
                {
                    if (!cbegin) putchar(ch);
                    puts("-\\n");
                    cbegin = 1;
                }
                else
                {
                    if (cbegin)
                    {
                        cbegin = 0;
                        putchar('-');
                    }
                    putchar(ch);
                }
            }
        }
#else
        (void) lastcbegin;
        (void) s;
#endif
	}
#undef ON_NEW_LINE
#define ON_NEW_LINE
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
#ifndef NO_HASH
    hash = top ? stackpathhash[top - 1] : DJB2_EMPTY_STR_HASH;
    DJB2_HASH_UPDATE(hash, '/');
#endif
    buf[0] = '/';
    bufpos = 1;
	while (isname(ch))
    {
        buf[bufpos++] = ch;
#ifndef NO_HASH
        DJB2_HASH_UPDATE(hash, ch);
#endif
        READ_CHAR_ROUTINE(ch);
    }
    CHECK_LIMIT(bufpos < BUFLEN);
    buf[bufpos] = '\0';
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (ch != '>') goto parse_end;
    --top;
    assert(top >= 0);
    lastpathpos = stackpathpos[top];
    assert(path[lastpathpos] == '/');
#ifndef NO_HASH
    if (hash != pathhash || strcmp(buf, path + lastpathpos))
#else
    if (strcmp(buf, path + lastpathpos))
#endif
    {
        errmsg = "closing element mismatch";
        goto parse_end;
    }
#ifndef NO_SHOW
    if (output && show)
    {
        printf(")%s\n", path + lastpathpos + 1);
#ifndef NO_HASH
        if (pathhash == showhash && strcmp(show, path) == 0)
#else
        if (strcmp(show, path) == 0)
#endif
        {
            output = 0;
        }
    }
#endif
    pathpos = lastpathpos;
    path[pathpos] = '\0';
#ifndef NO_HASH
    pathhash = stackpathhash[top];
#endif
	goto parse_text;

parse_element_name:
	errmsg = "syntax error in element name";
    lastpathpos = pathpos;
    stackpathpos[top] = pathpos;
#ifndef NO_HASH
    stackpathhash[top] = pathhash;
#endif
    ++top;
    CHECK_LIMIT(top < BUFLEN / sizeof(unsigned long));
    path[pathpos++] = '/';
#ifndef NO_HASH
    DJB2_HASH_UPDATE(pathhash, '/');
#endif
	while (isname(ch))
    {
        path[pathpos++] = ch;
#ifndef NO_HASH
        DJB2_HASH_UPDATE(pathhash, ch);
#endif
        READ_CHAR_ROUTINE(ch);
    }
    CHECK_LIMIT(pathpos < BUFLEN);
    path[pathpos] = '\0';
    if (!show)
    {
#ifndef SHOW_LINE_NUM
        puts(path);
#else
        printf("%s %" PRIu64 " %u\n", path, nLine, nCol);
#endif
    }
#ifndef NO_SHOW
#ifndef NO_HASH
    if (!output && show && pathhash == showhash && strcmp(show, path) == 0)
#else
    if (!output && show && strcmp(show, path) == 0)
#endif
    {
        output = 1;
    }
    if (output)
    {
#ifdef SHOW_LINE_NUM
        printf("(%s\n", path + lastpathpos + 1);
#else
        printf("(%s\n#L%" PRIu64 ".%u\n", path + lastpathpos + 1,
               nLine, nCol);
#endif
    }
#endif
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
#ifndef NO_SHOW
        if (output && show)
        {
            printf(")%s\n", path + lastpathpos + 1);
#ifndef NO_HASH
            if (pathhash == showhash && strcmp(show, path) == 0)
#else
            if (strcmp(show, path) == 0)
#endif
            {
                output = 0;
            }
        }
#endif
        pathpos = lastpathpos;
        path[pathpos] = '\0';
        --top;
        assert(top >= 0);
        lastpathpos = stackpathpos[top];
#ifndef NO_HASH
        pathhash = stackpathhash[top];
#endif
        goto parse_text;
    }
    goto parse_end;

parse_attribute_name:
	errmsg = "syntax error in attribute name";
#ifndef NO_SHOW
    if (output)
    {
        putchar('A');
        while (isname(ch))
        {
            putchar(ch);
            READ_CHAR_ROUTINE(ch);
        }
    }
    else
#endif
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
#ifndef NO_SHOW
    if (output)
    {
        putchar(' ');
        putchar(ch);
        if (ch == '"' || ch == '\'')
        {
            int quote = ch;
            do
            {
                READ_CHAR_ROUTINE(ch);
                putchar(ch);
            } while (ch != quote);
        }
        else
        {
            errmsg = "missing quote character";
            goto parse_end;
        }
        putchar('\n');
    }
    else
#endif
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
    free(stackpathpos);
#ifndef NO_HASH
    free(stackpathhash);
#endif
    if (errmsg)
    {
        return 1;
    }
    printf("#%" PRIu64 " lines processed\n", nLine);
    puts(")LBXG");
    return 0;
}

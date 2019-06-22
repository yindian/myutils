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
#include <ctype.h>
#if defined(__GNUC__) && __GNUC__ >= 7
#define FALL_THROUGH __attribute__((fallthrough))
#else
#define FALL_THROUGH /* fall through */
#endif
#ifdef __GNUC__
#define UNLIKELY(_x) __builtin_expect((_x), 0)
#else
#define UNLIKELY(_x) _x
#endif
#ifdef _WIN32
#define getchar _getchar_nolock
#define putchar _putchar_nolock
#define snprintf _snprintf
#else
#define getchar getchar_unlocked
#define putchar putchar_unlocked
#endif

#define BUFLEN 1024
#define BIGBUFLEN   1024 * 1024 * 4

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

static void showbuf(const char *buf, int buflen)
{
#if 1 /* CAVEAT: reporting the saved buf will badly penalize performance */
    const char *p, *end;
    const char **stacktagpos;
    int tagtop = 0;
    int cbegin = 1;
    stacktagpos = (const char **) malloc(BUFLEN);
    assert(stacktagpos);
    for (p = buf, end = buf + buflen; p < end; ++p)
    {
        int ch = *p;
        putchar(ch);
        if (ch == '\n')
        {
            cbegin = 1;
        }
        else if (cbegin)
        {
            if (ch == '(')
            {
                stacktagpos[tagtop++] = p + 1;
            }
            else if (ch == ')')
            {
                --tagtop;
            }
            cbegin = 0;
        }
    }
    if (p > buf && p[-1] != '\n')
    {
        putchar('\n');
    }
    if (tagtop > 0)
    {
        puts("#...");
        while (tagtop-- > 0)
        {
            putchar(')');
            for (p = stacktagpos[tagtop]; p < end && *p != '\n'; ++p)
            {
                putchar(*p);
            }
            putchar('\n');
        }
    }
    free(stacktagpos);
#endif
}

int main(int argc, char *argv[])
{
    uint64_t nLine2Show;
    uint64_t nLine;
    unsigned nCol;
    int i;
    int ch;
    int cbegin;
    int output;
    int help;
    int save, sameshowmatch;
    int check;
    int bufpos, pathpos, docpos;
    int lastbufpos;
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
    int patternlen;
#ifndef NO_HASH
    unsigned long showhash;
#endif
    output = 0;
    bufpos = pathpos = docpos = 0;
    lastbufpos = 0;
    lastpathpos = 0;
    top = 0;
#ifndef NO_HASH
    pathhash = DJB2_EMPTY_STR_HASH;
    showhash = DJB2_EMPTY_STR_HASH;
#endif
    help = 0;
    save = 0;
    check = 0;
    show = match = pattern = NULL;
    patternlen = 0;
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
        patternlen = strlen(pattern);
        if (!match)
        {
            char *p;
            nLine2Show = strtoull(pattern, &p, 0);
            help = (p && *p != '\0');
        }
        else if (!show)
        {
            show = match;
        }
    }
    sameshowmatch = show && match && strcmp(show, match) == 0;
    if (!help)
    {
        if (sameshowmatch)
        {
            /* not supported due to complexity */
            help = 1;
        }
        if (patternlen >= BUFLEN)
        {
            help = 1;
        }
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
        printf("as well as -m path if specified\n");
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
#if defined(NO_SHOW) || defined(NO_MATCH)
    (void) match;
    (void) nLine2Show;
    (void) save;
    (void) sameshowmatch;
#endif
#if defined(NO_SHOW) || defined(NO_MATCH) || defined(NO_CHECK)
    (void) check;
#else
    if (pattern)
    {
        char *p;
        for (p = (char *) pattern; *p; ++p)
        {
            *p = tolower(*p);
        }
    }
#endif
    buf = (char *) malloc(BUFLEN * 2);
    assert(buf);
    path = (char *) malloc(BUFLEN);
    assert(path);
    path[0] = '\0';
    doc = (char *) malloc(BIGBUFLEN);
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
#define SAVE(_c) doc[docpos++] = (_c)
#define SAVE2(_c, _d) SAVE(_c); SAVE(_d)
#ifdef _WIN32
    _setmode(_fileno( stdin ), _O_BINARY);
#endif
    nLine = 1;
    nCol = 0;
#define ON_NEW_LINE
#if !defined(NO_SHOW) && !defined(NO_MATCH)
#define ON_NEW_LINE_2 if (UNLIKELY(--nLine2Show == 0)) { \
    showbuf(doc, docpos); docpos = 0; save = 0; \
}
#else
    (void) showbuf;
#define ON_NEW_LINE_2
#endif
#define READ_CHAR_ROUTINE(_c) do \
    { \
        (_c) = getchar(); \
        if ((_c) == EOF) goto parse_end; \
        if ((_c) == '\n') {ON_NEW_LINE_2; ++nLine; nCol = 0; ON_NEW_LINE; } \
        else ++nCol; \
    } while (0)

parse_text:
    errmsg = NULL;
    bufpos = 0;
    cbegin = 1;
#undef ON_NEW_LINE
#ifndef NO_SHOW
#ifndef NO_MATCH
#define _ON_NEWLINE \
    if(output){if(!cbegin)putchar('\n');puts("-\\n");} \
    else if(save){if(!cbegin)SAVE('\n');SAVE2('-', '\\');SAVE2('n', '\n'); \
        if (docpos >= BUFLEN) { docpos = BUFLEN; save = 0; } \
    } \
    cbegin=1
#else
#define _ON_NEWLINE if(output){if(!cbegin)putchar('\n');puts("-\\n");} cbegin=1
#endif
#define ON_NEW_LINE _ON_NEWLINE
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
#define ON_NEW_LINE _ON_NEWLINE
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
#ifndef NO_MATCH
    else if (save)
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
                    SAVE('-');
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
                            SAVE(code);
                        }
                        else if (code < 0x800)
                        {
                            SAVE(0xC0 | (code >> 6));
                            SAVE(0x80 | (code & 0x3F));
                        }
                        else if (code < 0x10000)
                        {
                            SAVE(0xE0 | (code >> 12));
                            SAVE(0x80 | ((code >> 6) & 0x3F));
                            SAVE(0x80 | (code & 0x3F));
                        }
                        else if (code < 0x110000)
                        {
                            SAVE(0xF0 | (code >> 18));
                            SAVE(0x80 | ((code >> 12) & 0x3F));
                            SAVE(0x80 | ((code >> 6) & 0x3F));
                            SAVE(0x80 | (code & 0x3F));
                        }
                        else
                        {
                            break;
                        }
                        goto parse_entity_next_save;
                    } while (0);
                    errmsg = "unrecognized entity";
                    goto parse_end;
#undef ON_NEW_LINE
#define ON_NEW_LINE _ON_NEWLINE
                }
                else
                {
                    SAVE(ch);
                }
            }
        }
parse_entity_next_save:
        READ_CHAR_ROUTINE(ch);
    }
    if (!cbegin)
    {
        SAVE('\n');
    }
#if 0 /* disable checking for performance */
    if (docpos >= BUFLEN)
    {
        docpos = BUFLEN;
        save = 0;
    }
#endif
    }
#ifndef NO_CHECK
#undef ON_NEW_LINE
#define ON_NEW_LINE
#define CHECK_BUF_PATTERN \
    buf[bufpos] = '\0'; \
    if (strstr(buf, pattern)) \
    { \
        printf("#M%" PRIu64 ".%u: %s\n", nLine, nCol, buf); \
        showbuf(doc, docpos); \
        docpos = 0; \
        save = 0; \
        check = 0; \
        READ_CHAR_ROUTINE(ch); \
        goto parse_text_normal; \
    }
#define STORE(_c) buf[bufpos++] = (_c); if (bufpos == BUFLEN) { \
    CHECK_BUF_PATTERN; \
    memmove(buf, buf + BUFLEN - patternlen, patternlen); \
    bufpos = patternlen; \
}
    else if (check)
    {
        while (ch != '<')
        {
            if (ch == '&')
            {
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
                        STORE(tolower(code));
                    }
                    else if (code < 0x800)
                    {
                        STORE(0xC0 | (code >> 6));
                        STORE(0x80 | (code & 0x3F));
                    }
                    else if (code < 0x10000)
                    {
                        STORE(0xE0 | (code >> 12));
                        STORE(0x80 | ((code >> 6) & 0x3F));
                        STORE(0x80 | (code & 0x3F));
                    }
                    else if (code < 0x110000)
                    {
                        STORE(0xF0 | (code >> 18));
                        STORE(0x80 | ((code >> 12) & 0x3F));
                        STORE(0x80 | ((code >> 6) & 0x3F));
                        STORE(0x80 | (code & 0x3F));
                    }
                    else
                    {
                        break;
                    }
                    goto parse_entity_next_store;
                } while (0);
                errmsg = "unrecognized entity";
                goto parse_end;
            }
            else if (ch == '\n')
            {
                CHECK_BUF_PATTERN;
                bufpos = 0;
            }
            else
            {
                STORE(tolower(ch));
            }
parse_entity_next_store:
            READ_CHAR_ROUTINE(ch);
        }
    }
#endif
#endif
    else
#endif
    {
#if !defined(NO_SHOW) && !defined(NO_MATCH) && !defined(NO_CHECK)
parse_text_normal:
#endif
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
#ifndef NO_MATCH
            else if (save)
            {
                if (!cbegin)
                {
                    SAVE('\n');
                }
                if (docpos >= BUFLEN)
                {
                    docpos = BUFLEN;
                    save = 0;
                }
            }
#endif
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
#ifndef NO_MATCH
        else if (save)
        {
            char *p;
            cbegin = lastcbegin;
            for (p = s; (ch = *p); ++p)
            {
                if (ch == '\n')
                {
                    if (!cbegin) SAVE(ch);
                    SAVE2('-', '\\');SAVE2('n', '\n');
                    cbegin = 1;
                }
                else
                {
                    if (cbegin)
                    {
                        cbegin = 0;
                        SAVE('-');
                    }
                    SAVE(ch);
                }
            }
        }
#endif
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
    lastbufpos = bufpos;
    buf[bufpos++] = '/';
	while (isname(ch))
    {
        buf[bufpos++] = ch;
#ifndef NO_HASH
        DJB2_HASH_UPDATE(hash, ch);
#endif
        READ_CHAR_ROUTINE(ch);
    }
    CHECK_LIMIT(bufpos < BUFLEN * 2);
    buf[bufpos] = '\0';
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (ch != '>') goto parse_end;
    --top;
    assert(top >= 0);
    lastpathpos = stackpathpos[top];
    assert(path[lastpathpos] == '/');
#ifndef NO_HASH
    if (hash != pathhash || strcmp(buf + lastbufpos, path + lastpathpos))
#else
    if (strcmp(buf + lastbufpos, path + lastpathpos))
#endif
    {
        errmsg = "closing element mismatch";
        goto parse_end;
    }
    bufpos = lastbufpos;
#ifndef NO_SHOW
    if (output)
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
        else if (!pattern && match && strcmp(match, path) == 0)
        {
            output = 0;
        }
    }
#ifndef NO_MATCH
    else if (save && docpos >= BUFLEN)
    {
        docpos = BUFLEN;
        save = 0;
    }
    else if (save)
    {
        int ret;
        ret = snprintf(doc+docpos,BUFLEN-docpos, ")%s\n", path+lastpathpos+1);
        if (ret > 0) {
        docpos += ret;
        if (docpos >= BUFLEN)
        {
            docpos = BUFLEN;
            save = 0;
        }
        else
#ifndef NO_HASH
        if (pathhash == showhash && strcmp(show, path) == 0)
#else
        if (strcmp(show, path) == 0)
#endif
        {
            save = 0;
        }
        }
        else
        {
            save = 0;
        }
    }
#ifndef NO_CHECK
    if (check)
    {
        check = 0;
    }
#endif
#endif
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
#ifndef NO_MATCH
        if (pattern)
        {
            assert(!save);
            save = 1;
            docpos = 0;
        }
        else
#endif
        output = 1;
    }
    else if (!output && !pattern && match && strcmp(match, path) == 0)
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
#ifndef NO_MATCH
    else if (save && docpos >= BUFLEN)
    {
        docpos = BUFLEN;
        save = 0;
    }
    else if (save)
    {
        int ret;
#ifdef SHOW_LINE_NUM
        ret = snprintf(doc+docpos,BUFLEN-docpos, "(%s\n", path+lastpathpos+1);
#else
        ret = snprintf(doc+docpos,BUFLEN-docpos, "(%s\n#L%" PRIu64 ".%u\n",
                       path + lastpathpos + 1, nLine, nCol);
#endif
        if (ret > 0) {
        docpos += ret;
        if (docpos >= BUFLEN)
        {
            docpos = BUFLEN;
            save = 0;
        }
        }
        else
        {
            save = 0;
        }
    }
#ifndef NO_CHECK
    if (!check && pattern && match && strcmp(match, path) == 0)
    {
        check = 1;
        bufpos = 0;
    }
#endif
#endif
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
        if (output)
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
            else if (!pattern && match && strcmp(match, path) == 0)
            {
                output = 0;
            }
        }
#ifndef NO_MATCH
        else if (save)
        {
            int ret;
            ret = snprintf(doc+docpos,BUFLEN-docpos,")%s\n",path+lastpathpos+1);
            if (ret > 0) {
            docpos += ret;
            if (docpos >= BUFLEN)
            {
                docpos = BUFLEN;
                save = 0;
            }
            else
#ifndef NO_HASH
            if (pathhash == showhash && strcmp(show, path) == 0)
#else
            if (strcmp(show, path) == 0)
#endif
            {
                save = 0;
            }
            }
            else
            {
                save = 0;
            }
        }
#ifndef NO_CHECK
        if (check)
        {
            check = 0;
        }
#endif
#endif
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
#ifndef NO_MATCH
    else if (save)
    {
        SAVE('A');
        while (isname(ch))
        {
            SAVE(ch);
            READ_CHAR_ROUTINE(ch);
        }
        if (docpos >= BUFLEN)
        {
            docpos = BUFLEN;
            save = 0;
        }
    }
#endif
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
#ifndef NO_MATCH
    else if (save)
    {
        SAVE(' ');
        SAVE(ch);
        if (ch == '"' || ch == '\'')
        {
            int quote = ch;
            do
            {
                READ_CHAR_ROUTINE(ch);
                SAVE(ch);
            } while (ch != quote);
        }
        else
        {
            errmsg = "missing quote character";
            goto parse_end;
        }
        SAVE('\n');
        if (docpos >= BUFLEN)
        {
            docpos = BUFLEN;
            save = 0;
        }
    }
#endif
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

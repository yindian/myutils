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
    int i;
    int ch;
    int cbegin;
    int wrap, output;
    int help;
    int bufpos, pathpos, docpos;
    int lastpathpos;
    char *buf, *path, *doc;
    const char *errmsg;
    const char *show, *match, *pattern;
    wrap = output = 0;
    bufpos = pathpos = docpos = 0;
    lastpathpos = 0;
    help = 0;
    show = match = pattern = NULL;
    for (i = 1; i < argc; i++)
    {
        if (argv[i][0] == '-')
        {
            switch (argv[i][1])
            {
                case 's':
                    show = &argv[i][2];
                    break;
                case 'm':
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
        else
        {
            pattern = argv[i];
        }
    }
    if (pattern)
    {
        if (!match)
        {
            help = 1;
        }
    }
    else if (match)
    {
        match = NULL;
    }
    if (help)
    {
        printf("Line-Based Xml Grep by YIN Dian\n");
        printf("Usage: %s [-s/path/to/show] [-m/path/to/match] [pattern]\n",
               argv[0]);
        printf("Note: XML data is fed through stdin in a streaming manner\n");
        printf("Pattern is matched in character data under path of -m\n");
        printf("Without arguments, show element structure of the document\n");
        printf("Output in PYX notation, enhanced with / - path, # - note\n");
        return 0;
    }
    buf = (char *) malloc(BUFLEN);
    assert(buf);
    path = (char *) malloc(BUFLEN);
    assert(path);
    path[0] = '\0';
    doc = (char *) malloc(BUFLEN);
    assert(doc);
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
#define ON_NEW_LINE cbegin = 1
    READ_CHAR_ROUTINE(ch);
    while (ch != '<')
    {
        if (output)
        {
            if (cbegin)
            {
                if (!iswhite(ch))
                {
                    cbegin = 0;
                    putchar('-');
                    putchar(ch);
                }
            }
            else
            {
                putchar(ch);
            }
        }
        READ_CHAR_ROUTINE(ch);
    }
    if (output && !cbegin)
    {
        putchar('\n');
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
            if (output && !cbegin)
            {
                putchar('\n');
            }
            goto parse_text;
        } while (0);
        if (output)
        {
            char *p;
            cbegin = lastcbegin;
            for (p = s; (ch = *p); ++p)
            {
                if (cbegin)
                {
                    cbegin = 0;
                    putchar('-');
                }
                putchar(ch);
                if (ch == '\n')
                {
                    cbegin = 1;
                }
            }
        }
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
    if (output && show)
    {
        printf(")%s\n", path + lastpathpos + 1);
        if (strcmp(show, path) == 0)
        {
            output = 0;
        }
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
    if (show && strcmp(show, path) == 0)
    {
        printf("(%s\n", path + lastpathpos + 1);
        output = 1;
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
        if (output && show)
        {
            printf(")%s\n", path + lastpathpos + 1);
            if (strcmp(show, path) == 0)
            {
                output = 0;
            }
        }
        pathpos = lastpathpos;
        path[pathpos] = '\0';
        goto parse_text;
    }
    goto parse_end;

parse_attribute_name:
	errmsg = "syntax error in attribute name";
    if (output) putchar('A');
	while (isname(ch))
    {
        if (output) putchar(ch);
        READ_CHAR_ROUTINE(ch);
    }
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
	if (ch == '=') goto parse_attribute_value;
    goto parse_end;

parse_attribute_value:
	errmsg = "end of data in attribute value";
    READ_CHAR_ROUTINE(ch);
	while (iswhite(ch)) READ_CHAR_ROUTINE(ch);
    if (output)
    {
        putchar(' ');
        putchar(ch);
    }
    if (ch == '"')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (output) putchar(ch);
        } while (ch != '"');
    }
    else if (ch == '\'')
    {
        do
        {
            READ_CHAR_ROUTINE(ch);
            if (output) putchar(ch);
        } while (ch != '\'');
    }
    else
    {
		errmsg = "missing quote character";
        goto parse_end;
    }
    if (output) putchar('\n');
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
    printf("#%" PRIu64 " lines processed\n", nLine);
    puts(")LBXG");
    return 0;
}

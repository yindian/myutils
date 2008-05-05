// BBS Formatter ANSI C version, by YIN Dian on 08.5.4.
// Revised on 08.5.5.
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<ctype.h>
#include<getopt.h>
#include<assert.h>
//#include<windows.h>

#define GBK 0
#define UTF8 1
#define TRUE 1
#define FALSE 0
int o_join = FALSE;
int o_width = 74;
int o_maxwidth = 78;
int o_encoding = GBK;
int o_ansifilt = FALSE;
int o_prohibit = TRUE;
int o_expandtab = FALSE;
int o_tabsize = 4;

#define BUFSIZE 65536
#define S_INIT 0
#define S_READ 1
#define S_ANSI 2
#define S_NEWL 3
#define ISEXTENDCHAR(x) (x & 0x80)
typedef unsigned long wchar_utf8;
const char endansi[] = "\033[0m";
const wchar_utf8 linestartforbid_gbk[] = {
    44,     //,
    46,     //.
    58,     //:
    59,     //;
    33,     //!
    63,     //?
    41,     //)
    93,     //]
    125,    //}
    62,     //>
    41893,  //��
    41378,  //��
    41900,  //��
    41379,  //��
    41902,  //��
    41914,  //��
    41915,  //��
    41889,  //��
    41919,  //��
    41380,  //��
    41897,  //��
    41981,  //��
    41395,  //��
    41397,  //��
    41399,  //��
    41401,  //��
    41403,  //��
    41407,  //��
    41405,  //��
    41391,  //��
    41393,  //��
    0,
};
const wchar_utf8 lineendforbid_gbk[] = {
    40,    //(
    91,    //[
    123,   //{
    60,    //<
    36,    //$
    41896, //��
    41979, //��
    41394, //��
    41396, //��
    41398, //��
    41400, //��
    41402, //��
    41406, //��
    41404, //��
    41390, //��
    41392, //��
    0,
};
const wchar_utf8 intercharforbid_gbk[] = {
    41386,  //��
    41389,  //��
    43077,  //�E
    0,
};

const wchar_utf8 linestartforbid_utf8[] = {
    44,       //,
    46,       //.
    58,       //:
    59,       //;
    33,       //!
    63,       //?
    41,       //)
    93,       //]
    125,      //}
    62,       //>
    65285,    //％
    12289,    //、
    65292,    //，
    12290,    //。
    65294,    //．
    65306,    //：
    65307,    //；
    65281,    //！
    65311,    //？
    183,      //·
    65289,    //）
    65373,    //｝
    12309,    //〕
    12297,    //〉
    12299,    //》
    12301,    //」
    12303,    //』
    12305,    //】
    12311,    //〗
    8217,     //’
    8221,     //”
    0,
};
const wchar_utf8 lineendforbid_utf8[] = {
    40,      //(
    91,      //[
    123,     //{
    60,      //<
    36,      //$
    65288,   //（
    65371,   //｛
    12308,   //〔
    12296,   //〈
    12298,   //《
    12300,   //「
    12302,   //『
    12304,   //【
    12310,   //〖
    8216,    //‘
    8220,    //“
    0,
};
const wchar_utf8 intercharforbid_utf8[] = {
    8212,  //—
    8230,  //…
    8229,  //‥
    0,
};

const char trailingBytesForUTF8[256] = {
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, 3,3,3,3,3,3,3,3,4,4,4,4,5,5,5,5
};

int asserted_atoi(char *p)
{
        int result;
        char *endptr;
        result = strtol(p, &endptr, 10);
        if (*endptr == '\0')
                return result;
        fprintf(stderr, "Invalid number: %s\n", p);
        exit(-1);
}

int isgbk(int high, int low)
{
    return (high >= 0xA1 && high <= 0xA9 && low >= 0xA1 && low <= 0xFE)
        || (high >= 0xB0 && high <= 0xF7 && low >= 0xA1 && low <= 0xFE)
        || (high >= 0x81 && high <= 0xA0 && low >= 0x40 && low <= 0xFE)
        || (high >= 0xAA && high <= 0xFE && low >= 0x40 && low <= 0xA0)
        || (high >= 0xA8 && high <= 0xA9 && low >= 0x40 && low <= 0xA0);
}

int inwchararray(wchar_utf8 t, const wchar_utf8 ar[])
{
    int i = 0;
    while (ar[i] != 0)
        if (ar[i++] == t)
            return TRUE;
    return FALSE;
}

int breakable(wchar_utf8 buftext[], int bufpos, wchar_utf8 next)
{
#define ISSPACE(x) (x < 256 && isspace(x))
#define ISALNUM(x) (x < 256 && isalnum(x))
    if (bufpos < 1) // empty
        return FALSE;
    if (bufpos == 1 && ISSPACE(buftext[0])) // single blank char
        return TRUE;
    if (ISSPACE(next))
        return TRUE;
    if (!o_prohibit)
        return TRUE;
    if (o_encoding == GBK)
    {
        if (inwchararray(buftext[bufpos-1], lineendforbid_gbk)) // x(x
            return FALSE;
        if (inwchararray(buftext[bufpos-1], linestartforbid_gbk)) // x)x
            if (inwchararray(next, linestartforbid_gbk)) // x))
                return FALSE;
        if (inwchararray(next, linestartforbid_gbk)) // xx)
            return FALSE;
        if (inwchararray(buftext[bufpos-1], intercharforbid_gbk)
                && inwchararray(next, intercharforbid_gbk)) // x--
            return FALSE;
        if (ISALNUM(next) && ISALNUM(buftext[bufpos-1]))
            return FALSE;
    }
    else if (o_encoding == UTF8)
    {
        if (inwchararray(buftext[bufpos-1], lineendforbid_utf8)) // x(x
            return FALSE;
        if (inwchararray(buftext[bufpos-1], linestartforbid_utf8)) // x)x
            if (inwchararray(next, linestartforbid_utf8)) // x))
                return FALSE;
        if (inwchararray(next, linestartforbid_utf8)) // xx)
            return FALSE;
        if (inwchararray(buftext[bufpos-1], intercharforbid_utf8)
                && inwchararray(next, intercharforbid_utf8)) // x--
            return FALSE;
        if (ISALNUM(next) && ISALNUM(buftext[bufpos-1]))
            return FALSE;
    }
    else
    {
        fprintf(stderr, "Encoding not supported\n");
        exit(-1);
    }
    return TRUE;
}

char *code2utf8(wchar_utf8 code, char buf[])
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

void printbuf(int bufpos, wchar_utf8 buftext[])
{
    int i;
    if (o_encoding == GBK)
    {
        for (i = 0; i < bufpos; ++i)
            if (buftext[i] <= 0xff)
                printf("%c", (int)buftext[i]);
            else
                printf("%c%c", (int)(buftext[i]>>8), (int)(buftext[i] & 0xff));
    }
    else if (o_encoding == UTF8)
    {
        //int len;
        char result[16];
        for (i = 0; i < bufpos; ++i)
        {
            /*
            len = WideCharToMultiByte(CP_UTF8,0,buftext+i,1,NULL,0,NULL,FALSE);
            WideCharToMultiByte(CP_UTF8,0,buftext+i,1, result,len, NULL,FALSE);
            printf("%.*s", len, result);
            */
            printf("%s", code2utf8(buftext[i], result));
        }
    }
    else
    {
        fprintf(stderr, "Encoding not supported\n");
        exit(-1);
    }
}

void bbsformat(char *fname)
{
    FILE *fp;
    if (fname == NULL)
    {
        fp = stdin;
        fname = "(stdin)";
    }
    else
        fp = fopen(fname, "r");
    fprintf(stderr, "File %s\n", fname);
    if (fp == NULL)
    {
        fprintf(stderr, "Unable to open file %s\n", fname);
        return;
    }
    int status = S_INIT, currentpos = 0, bufwidth = 0, bufpos = 0;
    int ansipos = 0, extrabytes = -1;
    wchar_utf8 buftext[BUFSIZE] = {'0'};
    unsigned char lastchar;
    char ansitext[256] = {'0'};
    int ch, i, j;
    int lessnewline = FALSE, firstnewline = FALSE;
#define FLUSHBUF do{\
    currentpos += bufwidth;\
    if (currentpos > o_maxwidth)\
    {\
        for (i = 0; i < bufpos && buftext[i] == 32; ++i)\
            --bufwidth;\
        if (i > 0)\
            for (j = i; j < bufpos; ++j)\
                buftext[j-i] = buftext[j];\
        bufpos -= i;\
        _NEWLINE;\
        printbuf(bufpos, buftext);\
        currentpos = bufwidth; \
    }\
    else if (currentpos >= o_width)\
    {\
        printbuf(bufpos, buftext);\
        L_NEWLINE;\
        currentpos = 0;\
    }\
    else\
    {\
        if (!o_ansifilt && ansipos > 0 && lessnewline)\
            printf("%s", ansitext);\
        printbuf(bufpos, buftext);\
        lessnewline = FALSE;\
    }\
    bufpos = 0;\
    bufwidth = 0;\
}while(0)
#define _NEWLINE do{\
    if (!o_ansifilt && ansipos > 0)\
        printf("%s\n%s", endansi, ansitext);\
    else\
        printf("\n");\
    currentpos = 0;\
    lessnewline = FALSE;\
}while(0)
#define L_NEWLINE do{\
    if (!o_ansifilt && ansipos > 0)\
        printf("%s\n", endansi);\
    else\
        printf("\n");\
    currentpos = 0;\
    lessnewline = TRUE;\
}while(0)
#define NEWLINE do{\
    if (!lessnewline)\
        _NEWLINE;\
    else\
        lessnewline = FALSE;\
}while(0)
    while ((ch = fgetc(fp)) != EOF)
        switch (status)
        {
            case S_INIT:
l_s_init:
                if (ISEXTENDCHAR(ch))
                {
                    lastchar = ch;
                    status = S_READ;
                }
                else if (ch == '\r')
                {
                    if ((ch = fgetc(fp)) != '\n') // irregular newline in cmfu
                        ungetc(ch, fp);
                    if (!o_join)
                    {
                        if (bufpos > 0)
                            FLUSHBUF;
                        NEWLINE;
                    }
                    else
                        firstnewline = TRUE;
                    status = S_NEWL;
                }
                else if (ch == '\n')
                {
                    if (!o_join)
                    {
                        if (bufpos > 0)
                            FLUSHBUF;
                        NEWLINE;
                    }
                    else
                        firstnewline = TRUE;
                    status = S_NEWL;
                }
                else if (ch == '\t')
                {
                    if (bufpos > 0)
                        FLUSHBUF;
                    if (o_expandtab)
                        printf("%*c", (int)(currentpos / o_tabsize + 1) 
                                * o_tabsize - currentpos, ' ');
                    else
                        printf("\t");
                    status = S_INIT;
                }
                else if (ch == '\033')
                {
                    if (bufpos > 0)
                        FLUSHBUF;
                    ansipos = 0;
                    ansitext[ansipos++] = ch;
                    status = S_ANSI;
                }
                else // single width char
                {
                    if (breakable(buftext, bufpos, ch))
                        if (bufpos > 0)
                            FLUSHBUF;
                    buftext[bufpos++] = ch;
                    ++bufwidth;
                    status = S_INIT;
                }
                break;
            case S_READ:
                if (o_encoding == GBK)
                {
                    status = S_INIT;
                    if (isgbk(lastchar, ch))
                    {
                        ch = (lastchar << 8) | ch;
                        if (breakable(buftext, bufpos, ch))
                            if (bufpos > 0)
                                FLUSHBUF;
                        buftext[bufpos++] = ch;
                        bufwidth += 2;
                    }
                    else
                    {
                        buftext[bufpos++] = lastchar;
                        bufwidth += 1;
                        goto l_s_init;
                    }
                }
                else if (o_encoding == UTF8)
                {
                    if (extrabytes < 0) // new char, ch is second byte
                    {
                        extrabytes = trailingBytesForUTF8[(int)lastchar];
                        buftext[bufpos] = ((1<<(6-extrabytes))-1) & lastchar;
                    }
                    if (extrabytes <= 0) // invalid ansi char
                    {
                        buftext[bufpos++] = lastchar;
                        bufwidth += 1;
                        goto l_s_init;
                    }
                    buftext[bufpos] = (buftext[bufpos] << 6) | (ch & 0x3F);
                    if (--extrabytes == 0)
                    {
                        ch = buftext[bufpos];
                        if (breakable(buftext, bufpos, ch))
                            if (bufpos > 0)
                                FLUSHBUF;
                        buftext[bufpos++] = ch;
                        bufwidth += 2; // ambiguous?
                        status = S_INIT;
                        --extrabytes;
                    }
                }
                else
                {
                    fprintf(stderr, "Encoding not supported\n");
                    exit(-1);
                }
                break;
            case S_ANSI:
                if (ch == '\033') // duplicate escape
                    ;
                else
                {
                    ansitext[ansipos++] = ch;
                    if (ch == 'm')
                    {
                        ansitext[ansipos] = '\0';
                        status = S_INIT;
                        if (strcmp(ansitext, "\033[0m") == 0)
                        {
                            ansipos = 0;
                            if (currentpos > 0)
                            {
                                if (!o_ansifilt)
                                    printf("%s", ansitext);
                            }
                            else
                                lessnewline = TRUE;
                        }
                        else if (!o_ansifilt)
                            printf("%s", ansitext);
                    }
                }
                break;
            case S_NEWL:
                if (ch == '\r' || ch == '\n')
                {
                    
                    if (ch == '\r' && (ch = fgetc(fp)) != '\n')
                            ungetc(ch, fp);
                    if (o_join && firstnewline)
                    {
                        if (bufpos > 0)
                            FLUSHBUF;
                        NEWLINE;
                        firstnewline = FALSE;
                    }
                    NEWLINE;
                }
                else
                    goto l_s_init;
                break;
        }
    if (bufpos > 0)
        FLUSHBUF;
    if (!o_ansifilt && ansipos > 0)
        printf("%s", endansi);\
    fclose(fp);
}

int main(int argc, char *argv[])
{
    int ch, i;
    while ((ch = getopt(argc, argv, "jhw:W:uUAPts:")) != -1)
    {
        switch (ch) 
        {
            case 'j':
                o_join = TRUE;
                break;
            case 'w':
                o_width = asserted_atoi(optarg);
                break;
            case 'W':
                o_maxwidth= asserted_atoi(optarg);
                break;
            case 'u':
                o_encoding = UTF8;
                break;
            case 'A':
                o_ansifilt = TRUE;
                break;
            case 'P':
                o_prohibit = FALSE;
                break;
            case 't':
                o_expandtab = TRUE;
                break;
            case 's':
                o_tabsize = asserted_atoi(optarg);
                break;
            case 'h':
            case '?':
            default:
                goto l_showhelp;
        }
    }
    if (o_width < 2 || o_maxwidth < o_width || o_tabsize < 1)
        goto l_showhelp;
    argc -= optind;
    argv += optind;

    if (argc == 0)
        bbsformat(NULL);
    else
        for (i = 0; i < argc; ++i)
            bbsformat(argv[i]);

    return 0;

l_showhelp:
    printf("\
BBS Formatter lite v.080505     coded by YIN Dian\n\
Usage: %s [options] [filename(s)]\n\
By default, the input/output encoding is GBK, ANSI control sequences\n\
 not filtered, punctuation prohibitions considered, paragraph separated by\n\
 newlines, and tab not expanded. These options can be changed.\n\
Options:\n\
  -h, -?    Show help and quit.\n\
  -u        Set input/output encoding as UTF-8.\n\
  -A        Filter out ANSI control sequences.\n\
  -P        Do not consider punctuation prohibitions.\n\
  -j        Use blank line as paragraph delimiter (join lines).\n\
  -t        Expand tabs to spaces.\n\
  -s SIZE   Set tab size to SIZE (4 by default).\n\
  -w WIDTH     Set text wrapping width to WIDTH, default is 74\n\
  -W WIDTH     Set max width of a line to WIDTH, default is 78\n\
", argv[0]);
    return 0;
}


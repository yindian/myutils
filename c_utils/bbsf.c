// BBS Formatter ANSI C version, by YIN Dian
// Hist:    08.5.4. First coded.
//          08.5.5. Completed and revised. Fixed bug of tab offset.
//          08.5.7. Added invalid utf-8 sequence handling.
//                  Wrap the word when a word is longer than the line width.
//                  Changed some macros to functions.
//          08.5.12 Added encoding automatic detection.
//          08.5.13 Changed duplicate escape handling behavior.
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<ctype.h>
#include<getopt.h>
#include<assert.h>
//#include<windows.h>

#define GBK 0
#define UTF8 1
#define UNKNOWN 2
#define DEFAULTENC GBK
#define TRUE 1
#define FALSE 0
int o_join = FALSE;
int o_width = 74;
int o_maxwidth = 78;
int o_encoding = UNKNOWN;
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
char s_endansi[] = "\033\033[0m";
char *endansi = s_endansi + 1;
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
    41893,  //£•
    41378,  //°¢
    41900,  //£¨
    41379,  //°£
    41902,  //£Æ
    41914,  //£∫
    41915,  //£ª
    41889,  //£°
    41919,  //£ø
    41380,  //°§
    41897,  //£©
    41981,  //£˝
    41395,  //°≥
    41397,  //°µ
    41399,  //°∑
    41401,  //°π
    41403,  //°ª
    41407,  //°ø
    41405,  //°Ω
    41391,  //°Ø
    41393,  //°±
    0,
};
const wchar_utf8 lineendforbid_gbk[] = {
    40,    //(
    91,    //[
    123,   //{
    60,    //<
    36,    //$
    41896, //£®
    41979, //£˚
    41394, //°≤
    41396, //°¥
    41398, //°∂
    41400, //°∏
    41402, //°∫
    41406, //°æ
    41404, //°º
    41390, //°Æ
    41392, //°∞
    0,
};
const wchar_utf8 intercharforbid_gbk[] = {
    41386,  //°™
    41389,  //°≠
    43077,  //®E
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
    65285,    //ÔºÖ
    12289,    //„ÄÅ
    65292,    //Ôºå
    12290,    //„ÄÇ
    65294,    //Ôºé
    65306,    //Ôºö
    65307,    //Ôºõ
    65281,    //ÔºÅ
    65311,    //Ôºü
    183,      //¬∑
    65289,    //Ôºâ
    65373,    //ÔΩù
    12309,    //„Äï
    12297,    //„Äâ
    12299,    //„Äã
    12301,    //„Äç
    12303,    //„Äè
    12305,    //„Äë
    12311,    //„Äó
    8217,     //‚Äô
    8221,     //‚Äù
    0,
};
const wchar_utf8 lineendforbid_utf8[] = {
    40,      //(
    91,      //[
    123,     //{
    60,      //<
    36,      //$
    65288,   //Ôºà
    65371,   //ÔΩõ
    12308,   //„Äî
    12296,   //„Äà
    12298,   //„Ää
    12300,   //„Äå
    12302,   //„Äé
    12304,   //„Äê
    12310,   //„Äñ
    8216,    //‚Äò
    8220,    //‚Äú
    0,
};
const wchar_utf8 intercharforbid_utf8[] = {
    8212,  //‚Äî
    8230,  //‚Ä¶
    8229,  //‚Ä•
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

char *code2utf8(wchar_utf8 code, char *buf)
{
    char *q;
    static char _buf[16];
    if (buf == NULL)
        buf = _buf;
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

int currentpos = 0, bufwidth = 0, bufpos = 0, ansipos = 0;
wchar_utf8 buftext[BUFSIZE] = {'0'};
char ansitext[256] = {'0'};
int lessnewline = FALSE;

void _newline()
{
    if (!o_ansifilt && ansipos > 0)
        printf("%s\n%s", endansi, ansitext);
    else
        printf("\n");
    currentpos = 0;
    lessnewline = FALSE;
}
void l_newline()
{
    if (!o_ansifilt && ansipos > 0)
        printf("%s\n", endansi);
    else
        printf("\n");
    currentpos = 0;
    lessnewline = TRUE;
}
#define NEWLINE do{\
    if (!lessnewline)\
        _newline();\
    else\
        lessnewline = FALSE;\
}while(0)

void flushbuf()
{
    int i, j, k;
    currentpos += bufwidth;
    if (currentpos > o_maxwidth)
    {
        for (i = 0; i < bufpos && buftext[i] == 32; ++i)
            --bufwidth;
        if (bufwidth <= o_maxwidth)
        {
            if (i > 0)
                for (j = i; j < bufpos; ++j)
                    buftext[j-i] = buftext[j];
            bufpos -= i;
            _newline();
            printbuf(bufpos, buftext);
            currentpos = bufwidth; 
        }
        else
        {
            bufwidth += i;
            currentpos -= bufwidth;
            for (i = 0; bufwidth > o_maxwidth; i = j)
            {
                for (j=i,k=0; currentpos+k <= o_maxwidth && j < bufpos; ++j)
                    k += (buftext[j]>=128 ? 2 : 1); /* ambiguous? */
                if (j < bufpos || currentpos+k > o_maxwidth)
                    k -= (buftext[--j]>=128 ? 2 : 1);
                currentpos += k, bufwidth -= k;
                if (!o_ansifilt && ansipos > 0 && lessnewline)
                    printf("%s", ansitext);
                printbuf(j-i, buftext + i);
                l_newline();
            }
            if (i < bufpos)
            {
                assert(bufwidth <= o_maxwidth);
                if (!o_ansifilt && ansipos > 0 && lessnewline)
                    printf("%s", ansitext);
                printbuf(bufpos - i, buftext + i);
                currentpos = bufwidth; 
                lessnewline = FALSE;
            }
            else
                assert(bufwidth == 0);
        }
    }
    else if (currentpos >= o_width)
    {
        printbuf(bufpos, buftext);
        l_newline();
    }
    else
    {
        if (!o_ansifilt && ansipos > 0 && lessnewline)
            printf("%s", ansitext);
        printbuf(bufpos, buftext);
        lessnewline = FALSE;
    }
    bufpos = 0;
    bufwidth = 0;
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
    //fprintf(stderr, "File %s\n", fname);
    if (fp == NULL)
    {
        fprintf(stderr, "Unable to open file %s\n", fname);
        return;
    }
    int status = S_INIT, extrabytes = -1;
    unsigned char lastchar;
    int ch, firstnewline = FALSE;
    currentpos = 0, bufwidth = 0, bufpos = 0, ansipos = 0;
    lessnewline = FALSE;
    int encsave = o_encoding;
    endansi = s_endansi + 1;

    short charbuf[BUFSIZE] = {'\0'};
    int top = 0, i = 0;
    if (o_encoding == UNKNOWN)
    {
        int highcharcnt = 0, j;
        int gbkok = 0, gbkerror = 0, utf8ok = 0, utf8error = 0;
        while ((ch = fgetc(fp)) != EOF && highcharcnt < 200 && top < BUFSIZE-1
                && i < o_width)
        {
            charbuf[top++] = ch;
            if (ISEXTENDCHAR(ch))
                ++highcharcnt;
            ++i;
            if (ch == '\n' || ch == '\r')
                i = 0;
        }
        charbuf[top++] = ch;
        for (i = 0; i < top-1; ++i)
            if (ISEXTENDCHAR(charbuf[i]))
            {
                if (isgbk(charbuf[i], charbuf[i+1]))
                    ++gbkok, ++i;
                else
                    ++gbkerror;
            }
        for (i = 0; i < top-6; ++i)
            if (ISEXTENDCHAR(charbuf[i]))
            {
                if (trailingBytesForUTF8[(int)charbuf[i]] == 0)
                    ++utf8error;
                else
                {
                    for (j = 1; j <= trailingBytesForUTF8[(int)charbuf[i]]; ++j)
                        if ((charbuf[i+j] & 0xc0) != 0x80)
                        {
                            ++utf8error;
                            break;
                        }
                    i += j-1;
                    ++utf8ok;
                }
            }
        if (utf8ok > 0 && utf8error < utf8ok / 10)
            o_encoding = UTF8;
        else if (gbkok > 0 && gbkerror < gbkok / 10)
            o_encoding = GBK;
        else
            o_encoding = DEFAULTENC;
    }

    for (i = 0; (i<top && (ch=charbuf[i++]) != EOF) || (ch != EOF &&
			    (ch=fgetc(fp)) != EOF);)
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
                    //if ((ch = fgetc(fp)) != '\n') // irregular newline in cmfu
                    //    ungetc(ch, fp);
                    if (!o_join)
                    {
                        if (bufpos > 0)
                            flushbuf();
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
                            flushbuf();
                        NEWLINE;
                    }
                    else
                        firstnewline = TRUE;
                    status = S_NEWL;
                }
                else if (ch == '\t')
                {
                    if (bufpos > 0)
                        flushbuf();
                    if (o_expandtab)
                        printf("%*c", (int)(currentpos / o_tabsize + 1) 
                                * o_tabsize - currentpos, ' ');
                    else
                        printf("\t");
                    currentpos = (int)(currentpos / o_tabsize + 1) * o_tabsize;
                    status = S_INIT;
                }
                else if (ch == '\033')
                {
                    if (bufpos > 0)
                        flushbuf();
                    ansipos = 0;
                    ansitext[ansipos++] = ch;
                    status = S_ANSI;
                }
                else // single width char
                {
                    if (breakable(buftext, bufpos, ch))
                        if (bufpos > 0)
                            flushbuf();
                    assert(bufpos < BUFSIZE);
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
                                flushbuf();
                        assert(bufpos < BUFSIZE);
                        buftext[bufpos++] = ch;
                        bufwidth += 2;
                    }
                    else
                    {
                        fprintf(stderr, "Invalid char %c\n", lastchar);
                        assert(bufpos < BUFSIZE);
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
                        fprintf(stderr, "Invalid char %c\n", lastchar);
                        assert(bufpos < BUFSIZE);
                        buftext[bufpos++] = lastchar;
                        bufwidth += 1;
                        extrabytes = -1;
                        goto l_s_init;
                    }
                    if ((ch & 0xc0) == 0x80)
                        buftext[bufpos] = (buftext[bufpos] << 6) | (ch & 0x3F);
                    else
                    {
                        fprintf(stderr, "Invalid utf-8 seq %s\n", code2utf8(
                                    buftext[bufpos], NULL));
                        assert(bufpos < BUFSIZE);
                        bufpos++;
                        bufwidth += 2;
                        extrabytes = -1;
                        goto l_s_init;
                    }
                    if (--extrabytes == 0)
                    {
                        ch = buftext[bufpos];
                        if (breakable(buftext, bufpos, ch))
                            if (bufpos > 0)
                                flushbuf();
                        assert(bufpos < BUFSIZE);
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
                //if (ch == '\033') // duplicate escape
                //    ;
                //else
                {
                    if (ansipos == 1)
                        endansi = s_endansi + (ch != '\033');
                    ansitext[ansipos++] = ch;
                    if (ch == 'm')
                    {
                        ansitext[ansipos] = '\0';
                        status = S_INIT;
                        ch = ansitext[1] == '\033';
                        if (ansitext[ch+1] == '[' && 
                                ((ansitext[ch+2] == '0' &&
                                (ansitext[ch+3] == 'm' ||
                                ansitext[ch+3] == ';')) ||
                                ansitext[ch+2] == 'm'))
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
                    //if (ch == '\r' && (ch = fgetc(fp)) != '\n')
                    //    ungetc(ch, fp);
                    if (o_join && firstnewline)
                    {
                        if (bufpos > 0)
                            flushbuf();
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
        flushbuf();
    if (!o_ansifilt && ansipos > 0)
        printf("%s", endansi);
    o_encoding = encsave;
    fclose(fp);
}

int main(int argc, char *argv[])
{
    int ch, i;
    while ((ch = getopt(argc, argv, "jhw:W:ugAPts:")) != -1)
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
            case 'g':
                o_encoding = GBK;
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
BBS Formatter lite v.080513     coded by YIN Dian\n\
Usage: %s [options] [filename(s)]\n\
By default, the input/output encoding is auto-detected, ANSI control sequences\n\
 are not filtered, punctuation prohibitions are considered, paragraphs are\n\
 separated by newlines, and tabs are not expanded.\n\
Options:\n\
  -h, -?    Show help and quit.\n\
  -u        Set input/output encoding as UTF-8.\n\
  -g        Set input/output encoding as GBK.\n\
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


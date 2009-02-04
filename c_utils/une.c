#include<stdio.h>
#include<stdlib.h>
#include<ctype.h>
int main(int argc, char *argv[])
{
    char *p, s[3];
    int i, ch, c1, c2;
    if (argc > 1)
    {
        for (i = 1; i < argc; ++i)
        {
            if (i > 1)
                putchar(' ');
            for (p = argv[i]; *p; ++p)
            {
                do
                {
                    ch = *p;
                    if (*p != '%')
                        break;
                    if (!p[1] || !p[2])
                        break;
                    if (!isxdigit(p[1]) || !isxdigit(p[2]))
                        break;
                    s[0] = p[1];
                    s[1] = p[2];
                    s[2] = 0;
                    ch = strtol(s, NULL, 16);
                    p += 2;
                } while (0);
                putchar(ch);
            }
        }
    }
    else
    {
        while ((ch = getchar()) != EOF)
        {
            if (ch != '%')
            {
                putchar(ch);
                continue;
            }
            if ((c1 = getchar()) == EOF)
            {
                putchar(ch);
                ungetc(c1, stdin);
                continue;
            }
            if ((c2 = getchar()) == EOF || (!isxdigit(c1) || !isxdigit(c2)))
            {
                putchar(ch);
                putchar(c1);
                ungetc(c2, stdin);
                continue;
            }
            s[0] = c1;
            s[1] = c2;
            s[2] = 0;
            ch = strtol(s, NULL, 16);
            putchar(ch);
        }
    }
    return 0;
}

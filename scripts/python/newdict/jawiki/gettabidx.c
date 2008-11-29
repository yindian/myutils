#include<stdio.h>
#include<assert.h>
#define MAXKEYLEN 2048
int main(int argc, char *argv[])
{
    unsigned char buf[MAXKEYLEN] = {0};
    int ch;
    int pos = 0, tell = 0;
    FILE *fp;

    if (argc != 2)
    {
        printf("Usage: %s filename\nSort file by the key before the first tab\n", argv[0]);
        return 0;
    }

    fp = fopen(argv[1], "rb");
    assert(fp != NULL);
    assert(setvbuf(fp, NULL, _IOFBF, 20480) == 0);
    while ((ch = fgetc(fp)) != EOF)
    {
        if (ch == '\n')
        {
            pos = 0;
            tell = ftell(fp);
            assert(tell >= 0);
        }
        else if (ch == '\t')
        {
            buf[pos] = '\0';
            printf("%s\t%X\n", buf, tell);
            while ((ch = fgetc(fp)) != EOF && ch != '\n')
                ;
            pos = 0;
            tell = ftell(fp);
            assert(tell >= 0);
        }
        else
        {
            buf[pos++] = ch;
            if (pos >= MAXKEYLEN)
            {
                fprintf(stderr, "Error: pos exceed max len %d\n", MAXKEYLEN);
                printf("%.*s\n", MAXKEYLEN-1, buf);
                return 1;
            }
        }
    }
    fclose(fp);
    return 0;
}

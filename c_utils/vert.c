/*
 * Utility to format GBK text to reside vertically.
 * Usage: vert -w width -h height [-b num] [input file(s)]
 * -b: insert num blanks between columns
 */
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<getopt.h>
void showhelpandquit()
{
        printf("\
Utility to format GBK text to reside vertically.\n\
Usage: vert -w width -h height [-b num] [input file(s)]\n\
-b: insert num blanks between columns\n\
width should be greater than bnum + 1, height > 0\n");
        exit(0);
}
int asserted_atoi(char *p)
{
        int result;
        char *endptr;
        result = strtol(p, &endptr, 10);
        if (*endptr == '\0')
                return result;
        fprintf(stderr, "Invalid number: %s\n", p);
        showhelpandquit();
        exit(-1);
}
int width, height, bnum;
void vert(char fname[])
{
        char text[height][width];
        int xpos, ypos;
        FILE *fp;
        int ch;
        if (strcmp(fname, "-") == 0)
                fp = stdin;
        else
                fp = fopen(fname, "r");
        if (fp == NULL)
        {
                fprintf(stderr, "Unable to open file %s\n", fname);
                exit(-1);
        }
        for (ypos = 0; ypos < height; ++ypos)
                for (xpos = 0; xpos < width; ++xpos)
                        text[ypos][xpos] = ' ';
        xpos = width - bnum;
        ypos = 0;
        while ((ch = fgetc(fp)) != EOF)
        {
                if (ch & 0x80)  // extended ascii
                {
                        text[ypos][xpos - 2] = ch;
                        text[ypos][xpos - 1] = ch = fgetc(fp);
                        if (++ypos == height)
                        {
                                ypos = 0;
                                xpos -= bnum + 2;
                        }
                }
                else if (ch == '\r' || ch == '\n')
                {
                        ypos = 0;
                        xpos -= bnum + 2;
                        if (ch == '\r')
                        {
                                ch = fgetc(fp);
                                if (ch != '\n')
                                        ungetc(ch, fp);
                        }
                }
                else
                {
                        if (ch == '\t')
                                ch = ' ';
                        text[ypos][xpos - 1] = ch;
                        if (++ypos == height)
                        {
                                ypos = 0;
                                xpos -= bnum + 2;
                        }
                }
                if (xpos < 2) // one screen full
                {
                        for (ypos = 0; ypos < height; ++ypos)
                        {
                                for (xpos = 0; xpos < width; ++xpos)
                                {
                                        putchar(text[ypos][xpos]);
                                        text[ypos][xpos] = ' ';
                                }
                                printf("\n");
                        }
                        xpos = width - bnum;
                        ypos = 0;
                        printf("%c\n", 0x0c);
                }
        }
        if (xpos < width - bnum || ypos > 0) // one screen not full
        {
                for (ypos = 0; ypos < height; ++ypos)
                {
                        for (xpos = 0; xpos < width; ++xpos)
                        {
                                putchar(text[ypos][xpos]);
                                text[ypos][xpos] = ' ';
                        }
                        printf("\n");
                }
        }
}
int main(int argc, char *argv[])
{
        int ch, i;
        // initialization
        width = height = bnum = 0;
        // argument parsing
        while ((ch = getopt(argc, argv, "w:h:b:")) != -1)
        {
                switch (ch)
                {
                        case 'w':
                                width = asserted_atoi(optarg);
                                break;
                        case 'h':
                                height = asserted_atoi(optarg);
                                break;
                        case 'b':
                                bnum = asserted_atoi(optarg);
                                break;
                        case '?':
                        default:
                                showhelpandquit();
                }
        }
        if (width < bnum + 2 || height < 1)
                showhelpandquit();
        argc -= optind;
        argv += optind;
        // the main body
        if (argc == 0)
                vert("-");
        else
                for (i = 0; i < argc; ++i)
                        vert(argv[i]);
        return 0;
}

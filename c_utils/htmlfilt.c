// HTML escape sequence substituter
// Only support GBK
// Hist:	080610	First coded.
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<windows.h>
#define BUFS 16
const char *htmlunescape(char buf[])
{
	static char result[BUFS];
	if (buf[0] == '#')
	{
		int len;
		BOOL bad = FALSE;
		wchar_t code;
		char *p;
		code = strtol(buf+1, &p, 0);
		if (code == 8226)
			code = 183;
		len = WideCharToMultiByte(936,0,&code,1,NULL,0,NULL,&bad);
		if (p != NULL && *p == '\0' && !bad)
		{
			WideCharToMultiByte(936,0,&code,1, result,len, NULL,FALSE);
			result[len] = '\0';
		}
		else
			sprintf(result, "&%s;", buf);
	}
	else if (strcmp(buf, "amp") == 0)
		result[0] = '&', result[1] = '\0';
	else if (strcmp(buf, "nbsp") == 0)
		result[0] = ' ', result[1] = '\0';
	else if (strcmp(buf, "quot") == 0)
		result[0] = '"', result[1] = '\0';
	else if (strcmp(buf, "lt") == 0)
		result[0] = '<', result[1] = '\0';
	else if (strcmp(buf, "gt") == 0)
		result[0] = '>', result[1] = '\0';
	else
		sprintf(result, "&%s;", buf);
	return result;
}
int main()
{
	int ch;
	int status = 0, bufpos;
	char buf[BUFS];
	const char *p;
	while ((ch = fgetc(stdin)) != EOF)
		if (status == 0)
		{
			if (ch == '&')
				status = 1;
			else
				putchar(ch);
		}
		else if (status == 1)
		{
			if (ch == ';')
			{
				status = 0;
				putchar('&');
				putchar(ch);
			}
			else
			{
				status = 2;
				buf[0] = ch;
				bufpos = 1;
			}
		}
		else if (status == 2)
		{
			if (ch == ';')
			{
				buf[bufpos] = '\0';
				p = htmlunescape(buf);
                /*
				if (strcmp(p, "&") == 0)
					status = 1;
				else
                */
				{
					printf("%s", p);
					status = 0;
				}
			}
			else if (ch == 0xa3)
				status = 3;
			else if (bufpos >= BUFS)
			{
				printf("&%.*s", bufpos, buf);
				putchar(ch);
				status = 0;
			}
			else
				buf[bufpos++] = ch;
		}
		else if (status == 3)
		{
			if (ch == 0xbb)
			{
				buf[bufpos] = '\0';
				p = htmlunescape(buf);
				if (strcmp(p, "&") == 0)
					status = 1;
				else
				{
					printf("%s", p);
					status = 0;
				}
			}
			else
			{
				printf("&%.*s", bufpos, buf);
				putchar('\xa3');
				putchar(ch);
				status = 0;
			}
		}
	if (status > 0)
	{
		putchar('&');
		if (status > 1)
			printf("%.*s", bufpos, buf);
		if (status == 3)
			putchar('\xa3');
	}
	return 0;
}

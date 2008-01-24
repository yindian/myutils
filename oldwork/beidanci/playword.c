/*
 * 	Prog:	playword.c
 * 	Dscrptn:play out the sound of a given word
 * 	Auth:	Dian Yin
 * 	Hist:	05.07.21.
 */
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<ctype.h>
#define LINEMAXLEN 320
char player[LINEMAXLEN] = "mplayer";
char voicepath[LINEMAXLEN] = "C:/progra~1/stardict/sounds/";
void initialize()
{
	fclose(fopen(".tmp", "w"));
	freopen(".tmp", "r", stdin);
	freopen(".tmq", "w", stdout);
	freopen(".tmr", "w", stderr);

	if (voicepath[strlen(voicepath)-1] != '/')
		strcat(voicepath, "/");
}
int main(int argc, char *argv[])
{
	char str[LINEMAXLEN];
	int i;
	if (argc == 1)
	{
		printf("Usage: playword [word1] [word2] [...]");
		return 0;
	}
	initialize();
	for (i = 1; i < argc; ++i)
	{
		sprintf(str, "%s \"%s%c/%s.wav\"", player, voicepath, 
				tolower(argv[i][0]), strlwr(argv[i]));
#ifdef DEBUG
		fprintf(stderr, "%s\n", str);
#endif
		system(str);
	}
	return 0;
}

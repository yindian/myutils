/*
 * 	Prog:	beidanci.c
 * 	Auth:	Dian Yin
 * 	Dscrptn: Dian Yin's Word Memorizer
 * 	Hist:	05.07.17.
 * 		05.07.18.
 * 		05.07.21.	Added PrintList. Changed Memorize;
 * 				Added feature of playword in Memorize.
 * 		05.07.22.	Fixed bug in Test of printf("%d" => "%c"
 * 		05.07.21.	Added feature of repeating words when Memorize.
 * 		05.07.25.	Added printing out the totalwords when reselect interval.
 */
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<ctype.h>
#include<assert.h>
#include<time.h>
#define DO_NOTHING

#define DATAFILE "word.list"
#define LINEMAXLEN 320
struct _Node {
	char *word;
	char *meaning;
	struct _Node *next;
};
enum ECommand {unknown, printlist, memorize, test, changerange};
typedef struct _Node Node;
typedef Node *List;
List wordlist;

/*
 * 	Important notes:
 * 	This part of code is based on the following assumption. 
 * 	Other kind of data file may cause serious corruption.
 * 	1. each line in datafile has length less than LINEMAXLEN -1
 * 	2. word and meaning is seperated by blankss
 * 	3. every line is in the form of "\s*\S*\s*.*"
 */
void ReadData(int *totalwords)
{
	FILE *fp;
	Node *p, *q;
	char line[LINEMAXLEN];
	char *c, *d;
	*totalwords = 0;
	if ((fp = fopen(DATAFILE, "r")) == NULL)
	{
		fprintf(stderr, "Cannot open %s.\n", DATAFILE);
		exit(1);
	}
	assert(wordlist = (List)malloc(sizeof(Node)));
	p = q = wordlist;
	fgets(line, LINEMAXLEN, fp); 
	while (!feof(fp))
	{
		p = q;
		for (c = line; isspace(*c) && *c != '\0'; ++c)
			DO_NOTHING;
		for (d = c; !isspace(*d) && *d != '\n' && *d != '\0'; ++d)
			DO_NOTHING;
		*d = 0;
		assert(p->word = strdup(c));
		for (c = d+1; isspace(*c) && *c != '\0'; ++c)
			DO_NOTHING;
		for (d = c; *d != '\n' && *d != '\0'; ++d)
			DO_NOTHING;
		*d = 0;
		assert(p->meaning = strdup(c));
		++*totalwords;
		assert(q = (Node*)malloc(sizeof(Node)));
		p->next = q;

		fgets(line, LINEMAXLEN, fp);
	}
	free(q);
	if (p == wordlist)
		wordlist = NULL;
	else
		p->next = NULL;
	fclose(fp);
}

int SelectFromMenu(enum ECommand *command)
{
	int choice;
	printf("\
Welcome to use Dian Yin's Word Memorizer.\n\
Please select a command:\n\
0. Print out the word list.\n\
1. Memorize to the word list.\n\
2. Test your memory ^_*\n\
3. Change your word range.\n\
4. Quit.\n\
");
	while ( scanf("%d", &choice) != 1)
	{
		printf("Re-enter\n");
		fflush(stdin);
	}
	switch (choice)
	{
		case 0:
			*command = printlist;
			break;
		case 1:
			*command = memorize;
			break;
		case 2:
			*command = test;
			break;
		case 3:
			*command = changerange;
			break;
		case 4:
			return 0;
			break;
		default:
			*command = unknown;
	}
	return 1;
}

void setrange(int *llim, int *rlim, int totalwords)
{
	printf("There're totally %d words. What range do you want to memorize?\n", totalwords);
	do
	{
		printf("Please input left limit: ");
		while (scanf("%d", llim) != 1)
		{
			printf("Re-enter\n");
			fflush(stdin);
		}
		printf("Please input right limit: ");
		while (scanf("%d", rlim) != 1)
		{
			printf("Re-enter\n");
			fflush(stdin);
		}
	} while (!(*llim > 0 && *rlim >= *llim && *rlim <= totalwords));
}

/*
 * 	Notes: it is assumed that 0 < llim <= rlim <= totalwords
 * 	It only checks whether the input has two periods(.), if so , return
 */
void Memorize(int llim, int rlim, int playsound)
{
	Node *p;
	int i, ch, cnt, repeat;
	char str[LINEMAXLEN];
	fflush(stdin);
	printf("Now start memorizing words. Hit CR to continue after each word is shown. \'..\' to quit. \'<\' to repeat.\n");
	
	p = wordlist;
	for (i = 1; i < llim; ++i)
		p = p->next;
	for (; i <= rlim; )
	{
		printf("%d. %s  %s\n", i, p->word, p->meaning);
		if (playsound)
		{
			sprintf(str, "playword %s", p->word);
			system(str);
		}
		cnt = repeat = 0;
		while ((ch = getchar()) != '\n' && ch != EOF)
			if (ch == '.')
				++cnt;
			else if (ch == '<')
				repeat = 1;
		if (cnt >= 2)
			return;
		if (!repeat)
		{
			p = p->next;
			++i;
		}
	}
}

void PrintList(int llim, int rlim)
{
	Node *p;
	int i;
	
	p = wordlist;
	for (i = 1; i < llim; ++i)
		p = p->next;
	for (; i <= rlim; ++i)
	{
		printf("%d. %s  %s\n", i, p->word, p->meaning);
		p = p->next;
	}
}

/*
 * 	Notes: it is assumed that 0 < llim <= rlim <= totalwords
 * 	              and every word is less than LINEMAXLEN length.
 */
void Test(int llim, int rlim)	// randomly choose words to guess
{
	Node *base, *p;
	int i, t;
	int *used;
	char word[LINEMAXLEN];
	int ishint[LINEMAXLEN];
	int hintnum;
	fflush(stdin);
	printf("Now start testing words. Enter the correct word after each pause. \'..\' to quit.\n");
	printf("There're %d words to test. Get ready.\n", rlim - llim + 1);

	assert(used = (int*)malloc(sizeof(int) * (rlim-llim+1)));
	for (i = 0; i <= rlim - llim; ++i)
		used[i] = 0;
	base = wordlist;
	for (i = 1; i < llim; ++i)
		base = base->next;
	// Now base is the llim'th element
	for (i = llim; i <= rlim; ++i)
	{
		do
		{
			t = (int)((rlim-llim+1) * rand() / (RAND_MAX + 1.0));
		} while (used[t]);
		used[t] = 1;
		// now testing llim + t 'th word
		for (p = base; t > 0; --t)
			p = p -> next;
		// now t got another use ... ^o^
		// The way to test: 
		//  when strlen = 1, output _
		//  when strlen = 2, output x_
		//  else , output x____y
		printf("No %d. ", i - llim + 1);
		if (strlen(p->word) > 1)
			printf("%c", p->word[0]);
		for (t = 1; t < strlen(p->word)-1; ++t)
			if (isalpha(p->word[t]))
				printf("_");
			else printf("%c", p->word[t]);
		if (strlen(p->word) > 2)
			printf("%c", p->word[strlen(p->word)-1]);
		else
			printf("_");
		printf("  %s\n", p->meaning);
		do
		{
			printf("Try: ");
			scanf("%s", word);
			if (strcmp(word, "..") == 0)
			{
				free(used);
				return;
			}
			if (strcmp(word, p->word) == 0)
				printf("Correct! Good job!\n");
			else
			{
				printf("Uhh, please try again.");
				printf(" Hint: ");
				hintnum = 2 +  rand() % ((strlen(p->word)-2)/2+1);
				if (hintnum > strlen(p->word)-1)
					hintnum = strlen(p->word)-1;
				for (t = 0; t < strlen(p->word); ++t)
					ishint[t] = 0;
				while (hintnum--)
				{
					do
					{
						t =  (int)(strlen(p->word) * rand() / (RAND_MAX + 1.0));
					} while (ishint[t]);
					ishint[t] = 1;
				}
				for (t = 0; t < strlen(p->word); ++t)
					if (ishint[t])
						printf("%c", p->word[t]);
					else
						printf("_");
				printf("\n");
			}
		} while (strcmp(word, p->word) != 0);
	}

	free(used);
}
#ifdef DEBUG
void printwordlist()
{
	Node *p;
	fprintf(stderr, "Word List:\n");
	p = wordlist;
	while (p != NULL)
	{
		fprintf(stderr, "%s|%s\n", p->word, p->meaning);
		p = p->next;
	}
}
#endif
int main()
{
	int totalwords;
	int llim, rlim;
	int playsound;
	enum ECommand command;
	srand(time(NULL));
	ReadData(&totalwords);
	playsound = 1;
#ifdef DEBUG
	printwordlist();
#endif
	setrange(&llim, &rlim, totalwords);
	while (SelectFromMenu(&command))
	{
		if (command == memorize)
			Memorize(llim, rlim, playsound);
		else if (command == test)
			Test(llim, rlim);
		else if (command == changerange)
			setrange(&llim, &rlim, totalwords);
		else if (command == printlist)
			PrintList(llim, rlim);
	}
	printf("Thank you for using. Bye~~\n");
	return 0;
}

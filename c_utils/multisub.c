#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<malloc.h>
#include<assert.h>
#include<getopt.h>

/*************************************************************/
/*    GPL'ed getline implementation from wget, excerpt       */
/*************************************************************/
#ifndef EOVERFLOW
# define EOVERFLOW E2BIG
#endif
/* getdelim.c --- Implementation of replacement getdelim function.
   Copyright (C) 1994, 1996, 1997, 1998, 2001, 2003, 2005, 2006, 2007,
   2008, 2009 Free Software Foundation, Inc.
   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 3, or (at
   your option) any later version.
   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
   02110-1301, USA.  */
/* Ported from glibc by Simon Josefsson. */
#include <stdio.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#ifndef SSIZE_MAX
# define SSIZE_MAX ((ssize_t) (SIZE_MAX / 2))
#endif
#if USE_UNLOCKED_IO
# include "unlocked-io.h"
# define getc_maybe_unlocked(fp)        getc(fp)
#elif !HAVE_FLOCKFILE || !HAVE_FUNLOCKFILE || !HAVE_DECL_GETC_UNLOCKED
# undef flockfile
# undef funlockfile
# define flockfile(x) ((void) 0)
# define funlockfile(x) ((void) 0)
# define getc_maybe_unlocked(fp)        getc(fp)
#else
# define getc_maybe_unlocked(fp)        getc_unlocked(fp)
#endif
/* Read up to (and including) a DELIMITER from FP into *LINEPTR (and
   NUL-terminate it).  *LINEPTR is a pointer returned from malloc (or
   NULL), pointing to *N characters of space.  It is realloc'ed as
   necessary.  Returns the number of characters read (not including
   the null terminator), or -1 on error or EOF.  */
ssize_t
getdelim (char **lineptr, size_t *n, int delimiter, FILE *fp)
{
  ssize_t result;
  size_t cur_len = 0;
  if (lineptr == NULL || n == NULL || fp == NULL)
    {
      errno = EINVAL;
      return -1;
    }
  flockfile (fp);
  if (*lineptr == NULL || *n == 0)
    {
      char *new_lineptr;
      *n = 120;
      new_lineptr = (char *) realloc (*lineptr, *n);
      if (new_lineptr == NULL)
        {
          result = -1;
          goto unlock_return;
        }
      *lineptr = new_lineptr;
    }
  for (;;)
    {
      int i;
      i = getc_maybe_unlocked (fp);
      if (i == EOF)
        {
          result = -1;
          break;
        }
      /* Make enough space for len+1 (for final NUL) bytes.  */
      if (cur_len + 1 >= *n)
        {
          size_t needed_max =
            SSIZE_MAX < SIZE_MAX ? (size_t) SSIZE_MAX + 1 : SIZE_MAX;
          size_t needed = 2 * *n + 1;   /* Be generous. */
          char *new_lineptr;
          if (needed_max < needed)
            needed = needed_max;
          if (cur_len + 1 >= needed)
            {
              result = -1;
              errno = EOVERFLOW;
              goto unlock_return;
            }
          new_lineptr = (char *) realloc (*lineptr, needed);
          if (new_lineptr == NULL)
            {
              result = -1;
              goto unlock_return;
            }
          *lineptr = new_lineptr;
          *n = needed;
        }
      (*lineptr)[cur_len] = i;
      cur_len++;
      if (i == delimiter)
        break;
    }
  (*lineptr)[cur_len] = '\0';
  result = cur_len ? cur_len : result;
 unlock_return:
  funlockfile (fp); /* doesn't set errno */
  return result;
}

/* getline.c --- Implementation of replacement getline function.
   Copyright (C) 2005, 2006, 2007 Free Software Foundation, Inc.
   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 3, or (at
   your option) any later version.
   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
   02110-1301, USA.  */
/* Written by Simon Josefsson. */
ssize_t
getline (char **lineptr, size_t *n, FILE *stream)
{
  return getdelim (lineptr, n, '\n', stream);
}
/*************************************************************/
/*    GPL'ed getline implementation from wget  END           */
/*************************************************************/

typedef char *trie_t[256];

void trie_init(trie_t **root)
{
    assert(root);
    *root = (trie_t *) malloc(sizeof(trie_t));
    assert(*root);
    memset(*root, 0, sizeof(trie_t));
}

void trie_addstr(trie_t *root, const char *text, const char *nodeinfo)
{
    trie_t *node = root;
    unsigned char *p = (unsigned char *) text;
    assert(root && *root);
    assert(text && strlen(text));
    assert(nodeinfo);
    while (*p)
    {
        if (!node[0][*p])
        {
            node[0][*p] = (char *) malloc(sizeof(trie_t));
            assert(node[0][*p]);
            memset(node[0][*p], 0, sizeof(trie_t));
        }
        node = (trie_t *) node[0][*p];
        p++;
    }
    if (node[0][0])
        free(node[0][0]);
    node[0][0] = strdup(nodeinfo);
}

static void _trie_free_node(trie_t *node)
{
    int i;
    if (!node)
        return;
    for (i = 1; i < 256; i++)
    {
        _trie_free_node((trie_t *) node[0][i]);
        node[0][i] = NULL;
    }
    if (node[0][0])
        free(node[0][0]);
    free(node[0]);
}

void trie_free(trie_t **root)
{
    assert(root && *root);
    _trie_free_node(*root);
    *root = NULL;
}

void multisub(trie_t *root, FILE *inf, FILE *outf, int buflen)
{
    trie_t *node = root;
    char *buf;
    int bufpos = 0, i, pend = 0, pendpos = 0;
    int ch;
    buf = (char *) malloc(buflen);
    assert(buf);
    memset(buf, 0, buflen);
    while ((ch = (pendpos < pend ? buf[pendpos++] : getc(inf))) != EOF)
    {
        if (ch == '\0')
            putc(ch, outf);
        else if (node[0][ch])
        {
            buf[bufpos++] = ch;
            node = (trie_t *) node[0][ch];
            if (node[0][0]) /* has pattern */
            {
                fputs(node[0][0], outf);
                node = root;
#ifdef DEBUG
                memset(buf, 0, buflen);
#endif
                bufpos = 0;
            }
        }
        else if (!bufpos)
        {
            putc(ch, outf);
        }
        else
        {
            putc(buf[0], outf);
            node = root;
#ifdef DEBUG
            buf[0] = '\0';
#endif
            buf[bufpos++] = ch;
            pend = bufpos;
            pendpos = 1;
            bufpos = 0;
        }
    }
    for (i = 0; i < bufpos; i++)
        putc(buf[i], outf);
    free(buf);
}

int main(int argc, char *argv[])
{
    FILE *fp = NULL;
    int i, ch, l, help=0, verbose=0;
    char *delimiter = "->";
    char *line = NULL, *p;
    size_t len = 0;
    trie_t *trie = NULL;
    int maxpatlen = 0;

    setvbuf(stdout, NULL, _IOFBF, 16384);

    while ((ch = getopt(argc, argv, "d:h?v")) != EOF)
        switch (ch)
        {
            case 'h':
            case '?':
                help = 1;
                break;
            case 'd':
                delimiter = strdup(optarg);
                break;
            case 'v':
                verbose = 1;
                break;
        }

    if (argc - optind < 1 || help)
    {
        printf("Multiple string replacement filter. stdin->stdout\n");
        printf("Usage: %s [-d delimiter] pattern_file\n", argv[0]);
        printf("Each line in pattern_file is a from-to pair, delimited by -> by default\n");
        return 0;
    }
    if (verbose)
        fprintf(stderr, "Reading pattern file.\n");
    fp = fopen(argv[optind], "r");
    if (!fp)
    {
        fprintf(stderr, "Failed open file %s", argv[optind]);
        return 1;
    }
    l = strlen(delimiter);
    trie_init(&trie);
    while (getline(&line, &len, fp) != EOF)
    {
        p = strchr(line, '\n');
        if (p)
            *p = '\0';
        p = strstr(line, delimiter);
        if (!p)
            fprintf(stderr, "ignoring pattern not paired: %s\n", line);
        else if (p == line)
            fprintf(stderr, "ignoring empty pattern: %s\n", line);
        else
        {
            *p = '\0';
            trie_addstr(trie, line, p+l);
            i = strlen(line);
            if (i > maxpatlen)
                maxpatlen = i;
        }
    }
    fclose(fp);
    if (verbose)
        fprintf(stderr, "Finished building trie from patterns.\n");

    multisub(trie, stdin, stdout, maxpatlen);

    if (verbose)
        fprintf(stderr, "Done.\n");
    trie_free(&trie);
    return 0;
}

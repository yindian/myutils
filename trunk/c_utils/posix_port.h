#ifndef _POSIX_PORT_H
#define _POSIX_PORT_H
#include <stdio.h>
#include <wchar.h>
int _wmkdir(const wchar_t *wpath);
FILE *_wfopen(const wchar_t *wpath, const wchar_t *wmode);
int getch();
#define fgetws _fgetws
#endif

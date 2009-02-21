#ifndef MYRUSAGE_H
#define MYRUSAGE_H

#include <sys/time.h>           /* for struct timeval */
#include <limits.h>             /* for CLK_TCK */
#include <errno.h>
#include <windows.h>
#include <stdio.h>

#define RUSAGE_SELF     0
#define RUSAGE_CHILDREN (-1)

struct rusage
{
    struct timeval ru_utime;    /* user time used */
    struct timeval ru_stime;    /* system time used */
};

static int  getrusage(int who, struct rusage * rusage);

static void _dosmaperr(unsigned long e);

int
getrusage(int who, struct rusage * rusage)
{
    FILETIME    starttime;
    FILETIME    exittime;
    FILETIME    kerneltime;
    FILETIME    usertime;
    ULARGE_INTEGER li;

    if (rusage == (struct rusage *) NULL)
    {
        errno = EFAULT;
        return -1;
    }
    memset(rusage, 0, sizeof(struct rusage));
    if (GetProcessTimes(GetCurrentProcess(),
                        &starttime, &exittime, &kerneltime, &usertime) == 0)
    {
        _dosmaperr(GetLastError());
        return -1;
    }

    /* Convert FILETIMEs (0.1 us) to struct timeval */
    memcpy(&li, &kerneltime, sizeof(FILETIME));
    li.QuadPart /= 10L;         /* Convert to microseconds */
    rusage->ru_stime.tv_sec = li.QuadPart / 1000000L;
    rusage->ru_stime.tv_usec = li.QuadPart % 1000000L;

    memcpy(&li, &usertime, sizeof(FILETIME));
    li.QuadPart /= 10L;         /* Convert to microseconds */
    rusage->ru_utime.tv_sec = li.QuadPart / 1000000L;
    rusage->ru_utime.tv_usec = li.QuadPart % 1000000L;

    return 0;
}

#define _(x) x
#define lengthof(x) (sizeof(x) / sizeof(x[0]))

static const struct
{
    DWORD       winerr;
    int         doserr;
}   doserrors[] =

{
    {
        ERROR_INVALID_FUNCTION, EINVAL
    },
    {
        ERROR_FILE_NOT_FOUND, ENOENT
    },
    {
        ERROR_PATH_NOT_FOUND, ENOENT
    },
    {
        ERROR_TOO_MANY_OPEN_FILES, EMFILE
    },
    {
        ERROR_ACCESS_DENIED, EACCES
    },
    {
        ERROR_INVALID_HANDLE, EBADF
    },
    {
        ERROR_ARENA_TRASHED, ENOMEM
    },
    {
        ERROR_NOT_ENOUGH_MEMORY, ENOMEM
    },
    {
        ERROR_INVALID_BLOCK, ENOMEM
    },
    {
        ERROR_BAD_ENVIRONMENT, E2BIG
    },
    {
        ERROR_BAD_FORMAT, ENOEXEC
    },
    {
        ERROR_INVALID_ACCESS, EINVAL
    },
    {
        ERROR_INVALID_DATA, EINVAL
    },
    {
        ERROR_INVALID_DRIVE, ENOENT
    },
    {
        ERROR_CURRENT_DIRECTORY, EACCES
    },
    {
        ERROR_NOT_SAME_DEVICE, EXDEV
    },
    {
        ERROR_NO_MORE_FILES, ENOENT
    },
    {
        ERROR_LOCK_VIOLATION, EACCES
    },
    {
        ERROR_SHARING_VIOLATION, EACCES
    },
    {
        ERROR_BAD_NETPATH, ENOENT
    },
    {
        ERROR_NETWORK_ACCESS_DENIED, EACCES
    },
    {
        ERROR_BAD_NET_NAME, ENOENT
    },
    {
        ERROR_FILE_EXISTS, EEXIST
    },
    {
        ERROR_CANNOT_MAKE, EACCES
    },
    {
        ERROR_FAIL_I24, EACCES
    },
    {
        ERROR_INVALID_PARAMETER, EINVAL
    },
    {
        ERROR_NO_PROC_SLOTS, EAGAIN
    },
    {
        ERROR_DRIVE_LOCKED, EACCES
    },
    {
        ERROR_BROKEN_PIPE, EPIPE
    },
    {
        ERROR_DISK_FULL, ENOSPC
    },
    {
        ERROR_INVALID_TARGET_HANDLE, EBADF
    },
    {
        ERROR_INVALID_HANDLE, EINVAL
    },
    {
        ERROR_WAIT_NO_CHILDREN, ECHILD
    },
    {
        ERROR_CHILD_NOT_COMPLETE, ECHILD
    },
    {
        ERROR_DIRECT_ACCESS_HANDLE, EBADF
    },
    {
        ERROR_NEGATIVE_SEEK, EINVAL
    },
    {
        ERROR_SEEK_ON_DEVICE, EACCES
    },
    {
        ERROR_DIR_NOT_EMPTY, ENOTEMPTY
    },
    {
        ERROR_NOT_LOCKED, EACCES
    },
    {
        ERROR_BAD_PATHNAME, ENOENT
    },
    {
        ERROR_MAX_THRDS_REACHED, EAGAIN
    },
    {
        ERROR_LOCK_FAILED, EACCES
    },
    {
        ERROR_ALREADY_EXISTS, EEXIST
    },
    {
        ERROR_FILENAME_EXCED_RANGE, ENOENT
    },
    {
        ERROR_NESTING_NOT_ALLOWED, EAGAIN
    },
    {
        ERROR_NOT_ENOUGH_QUOTA, ENOMEM
    }
};

void
_dosmaperr(unsigned long e)
{
    int         i;

    if (e == 0)
    {
        errno = 0;
        return;
    }

    for (i = 0; i < lengthof(doserrors); i++)
    {
        if (doserrors[i].winerr == e)
        {
            errno = doserrors[i].doserr;
            fprintf(stderr, _("mapped win32 error code %lu to %d"), e, errno);
            return;
        }
    }

    fprintf(stderr, _("unrecognized win32 error code: %lu"), e);

    errno = EINVAL;
    return;
}

#endif   /* MYRUSAGE_H */

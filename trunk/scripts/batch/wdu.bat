@echo off
if "%1" == "-s" goto summarize
echo Usage: %0 -s [wildchar]
echo Display space usage of directories
goto end

:summarize
shift
if not "%1" == "" goto loop_sum
diskuse /s | findstr /c:"Space Used"
goto end

:loop_sum
::if exist "%1" (
::printf "%1\t"
::diskuse /s "%1" | findstr /c:"Space Used" | gawk "{print $3}"
::goto next_sum
::)
for /d %%c in ("%1") do (
printf "%%c\t"
diskuse /s "%%c" | findstr /c:"Space Used" | gawk "{print $3}"
)

:next_sum
shift
if not "%1" == "" goto loop_sum

:end

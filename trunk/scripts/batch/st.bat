@echo off
if "%1"=="" goto help
if "%1"=="rec" goto commit
if "%1"=="all" goto all
if "%1"=="touch" goto touch
:help
echo Usage: %0 command
echo.
echo Commands:
echo   rec: save timestamps of changed file, and do darcs rec
echo   all: save timestamps of all the files managed by darcs
echo touch: apply saved timestamps to all the files managed
echo.
echo Both commands work on the files in the current directory
echo Changed files are listed by darcs wha -s, file listed by darcs sh f
goto end
:commit
darcs wha -s > %0.tmp
if errorlevel 1 goto error
darcs wha -s | sed "s/^[^M]/&/;t;s/\( [+-][0-9]*\)\{1,2\}//" | sed "s+/$++;s+/+\\+g;s/^\w //" > %0.tmp
for /f %%c in (%0.tmp) do @if not exist %%c goto error
if exist %0.dat type %0.dat > %0.old
type %0.tmp
for /f %%c in (%0.tmp) do @(
  ufind %%c -prune -printf "%%TY%%Tm%%Td%%TH%%TM.%%TS %%p\n"
) >> %0.dat
type %0.dat | usort -k 2 > %0.tmp
type %0.tmp | uniq -f 1 > %0.dat
del %0.tmp
echo OK
darcs %*
goto end
:all
darcs sh f > %0.tmp
if errorlevel 1 goto error
darcs sh f | sed "1d;s+/$++;s+/+\\+g" > %0.tmp
for /f %%c in (%0.tmp) do @if not exist %%c goto error
if exist %0.dat type %0.dat > %0.old
type %0.tmp
type nul > %0.dat
for /f %%c in (%0.tmp) do @(
  ufind %%c -prune -printf "%%TY%%Tm%%Td%%TH%%TM.%%TS %%p\n"
) >> %0.dat
type %0.dat | usort -k 2 > %0.tmp
type %0.tmp > %0.dat
del %0.tmp
echo OK
goto end
:touch
for /f "tokens=1*" %%c in (%0.dat) do @if not exist %%d goto error
for /f "tokens=1*" %%c in (%0.dat) do @(
  echo Touching %%d ...
  touch -t %%c "%%d"
)
echo OK
goto end
:error
echo An error occurred. May be darcs is not properly configured or current directory incorrect.
del %0.tmp
goto end
:end

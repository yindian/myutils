@echo off
if "%1"=="" goto end
if not exist "%1" goto end
if "%2"=="" (
for %%c in (%1) do (
set CUEFILE=%%~nc.cue
)
) else set CUEFILE=%2
echo %1 %CUEFILE%
cuebreakpoints --split-gaps %CUEFILE% > .tmp
shntool split -O always "%1" -f .tmp -o "cust ext=m4a neroaacenc -br 32768 -if - -of %%f"

grep INDEX %CUEFILE% | head -1 | gawk "{print $2, $3;}" > .tmp2
set FIRST=0:00.00
for /f %%d in (.tmp2) do @(
if not "%%d"=="01" for /f %%e in ('head -1 .tmp') do @set FIRST=%%e
)

echo %FIRST%> .tmp
cuebreakpoints %CUEFILE% >> .tmp
cat -n .tmp > .tmp2
echo 0:00.00> .tmp
cuebreakpoints --split-gaps %CUEFILE% >> .tmp

rem for /f %%d in ('wc -l .tmp2') do @set /a TRACKNUM=%%d+1
type nul > .tmp.bat
for /f "tokens=1,*" %%d in (.tmp2) do @(
for /f "delims=:" %%f in ('grep -n %%e .tmp') do @(
echo %%d: track num, %%f: file num
if %%f LSS 10 (
  printf "move split-track0%%f.m4a " >> .tmp.bat
  for /f "tokens=*" %%g in ('cueprint -n %%d -t "%%t" %CUEFILE%') do @(
  neroaactag split-track0%%f.m4a -meta:title="%%g" 2> nul
  )
  for /f "tokens=*" %%g in ('cueprint -n %%d -t "%%p" %CUEFILE%') do @(
  neroaactag split-track0%%f.m4a -meta:artist="%%g" 2> nul
  )
) else (
printf "move split-track%%f.m4a " >> .tmp.bat
  for /f "tokens=*" %%g in ('cueprint -n %%d -t "%%t" %CUEFILE%') do @(
  neroaactag split-track%%f.m4a -meta:title="%%g" 2> nul
  )
  for /f "tokens=*" %%g in ('cueprint -n %%d -t "%%p" %CUEFILE%') do @(
  neroaactag split-track%%f.m4a -meta:artist="%%g" 2> nul
  )
)
for /f "tokens=*" %%g in (
  'cueprint -n %%d -t "%%02n. %%t - %%p.m4a\n" %CUEFILE%') do @(
  echo "%%g">> .tmp.bat
)
)
)
call .tmp.bat
:end

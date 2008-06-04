@echo off
if ".%1"=="." goto help
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt *.html
echo Getting index...
set myurl=%1
if "%myurl:~-2%"=="kz" set myurl=%1=%2
echo url=%myurl%
wget %myurl% -O list.html
echo -e -s -c ":so tiebaindex.vim" -c ":sav index.txt" -c ":q" list.html
%myvim% -e -s -c ":so tiebaindex.vim" -c ":sav index.txt" -c ":q" list.html
echo Done processing index.
echo Fetching pages...
rem wget -nc -i index.txt
rem for %%c in (f@kz*) do @(
for /f %%c in (index.txt) do @(
    echo Processing %%c ...
    wget -nv -c %%c
rem    %myvim% -e -s -c ":so tieba.vim" -c ":sav %%:r.txt" -c ":q" "%%c"
    %myvim% -e -s -c ":so tieba.vim" -c ":sav %%:r.txt" -c ":q" "%%~nc"
)
echo Done fetching pages and processing texts.
type nul > novel.txt
for /f "tokens=1*" %%c in (index.txt) do @(
    echo filename=%%c.txt
    type %%~nc.txt >> novel.txt
)
goto end
:help
echo Usage: %0 [Tieba URL]
:end

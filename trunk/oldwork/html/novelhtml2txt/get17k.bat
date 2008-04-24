@echo off
if ".%1"=="." goto help
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
set encconv=-c ":set fenc=cp936"
del *.txt
echo Getting index...
wget -nc "http://www.17k.com/list/%1.html" -O list.html
echo -e -s -c ":so 17kindex.vim" %encconv% -c ":sav index.txt" -c ":q" list.html
%myvim% -e -s -c ":so 17kindex.vim" %encconv% -c ":sav index.txt" -c ":q" list.html
echo Done processing index.
echo Fetching pages...
grep "a title" list.html | sed "s/^.*href=.\(.*\).>.*$/http:\/\/www.17k.com\/\1/" > list
wget -nc -i list
for %%c in (*.shtml) do @(
    echo Processing %%c ...
    %myvim% -e -s -c ":so yiqikan.vim" %encconv% -c ":sav %%:r.txt" -c ":q" "%%c"
)
echo Done fetching pages and processing texts.
type nul > novel.txt
for /f "tokens=1*" %%c in (index.txt) do @(
    if "%%d"=="" (
        echo chapter=%%c
        echo WSCHAPTER%%c >> novel.txt
    ) else (
        if exist %%c.txt (
            echo filename=%%c.txt   name=%%d
            echo WSSECTION%%d >> novel.txt
            type %%c.txt >> novel.txt
        ) else (
            echo chapter=%%c %%d
            echo WSCHAPTER%%c %%d >> novel.txt
        )
    )
)
goto end
:help
echo Usage: %0 [Book Number in 17k]
:end

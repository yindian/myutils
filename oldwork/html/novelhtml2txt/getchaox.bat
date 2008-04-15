@echo off
if ".%1"=="." goto help
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt *.js
echo Getting index...
wget "http://origin.ssreader.com/worksmenu/%1.txt" -O index.js
echo -e -s -c ":so cxindex.vim" -c ":sav index.txt" -c ":q" index.js
%myvim% -e -s -c ":so cxindex.vim" -c ":sav index.txt" -c ":q" index.js
echo Done processing index.
echo Fetching pages and processing...
for /f "tokens=1*" %%c in (index.txt) do @(
    if "%%d"=="" (
        echo chapter=%%c
    ) else (
            echo filename=%%c   name=%%d
            wget "http://origin.ssreader.com/workscontent/cp/%1/%%c.txt" -O "%%c.js"
            if exist %%c.js %myvim% -e -s -c ":so chaoxing.vim" -c ":sav %%c.txt" -c ":q" "%%c.js"
    )
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
echo Usage: %0 [Book Number in Chaoxing Yuanchuang]
:end

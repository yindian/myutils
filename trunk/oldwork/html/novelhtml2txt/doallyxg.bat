@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt
for %%c in (*.html) do @(
    echo Processing %%c ...
    %myvim% -e -s -c ":so yunxiaoge.vim" -c ":sav %%:r.txt" -c ":q" "%%c"
)
echo Done processing texts.
del index.txt
echo Processing index ...
echo -e -s -c ":so yxgindex.vim" -c ":sav index.txt" -c ":q" index.html
%myvim% -e -s -c ":so yxgindex.vim" -c ":sav index.txt" -c ":q" index.html
echo Done processing index.
findstr id=\"title\" index.html > title
%myvim% -e -s -c ":s/<.\{-}>\(.*\)<.*/WSTITLE\1/g" -c ":wq" title
echo Done getting title.
rem type nul > novel.txt
type title > novel.txt
for /f "tokens=1*" %%c in (index.txt) do @(
    if "%%d"=="" (
        echo chapter=%%c
        echo WSCHAPTER%%c >> novel.txt
    ) else (
        if exist %%c (
            echo filename=%%c   name=%%d
            echo WSSECTION%%d >> novel.txt
            type %%c >> novel.txt
        ) else (
            echo chapter=%%c %%d
            echo WSCHAPTER%%c %%d >> novel.txt
        )
    )
)

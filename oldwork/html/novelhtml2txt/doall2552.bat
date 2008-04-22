@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt
for %%c in (*.shtml) do @(
    echo Processing %%c ...
    %myvim% -e -s -c ":so wuaiwenxue.vim" -c ":sav %%:r.txt" -c ":q" "%%c"
)
echo Done processing texts.
del index.txt
echo Processing index ...
echo -e -s -c ":so wawxindex.vim" -c ":sav index.txt" -c ":q" List.shtml
%myvim% -e -s -c ":so wawxindex.vim" -c ":sav index.txt" -c ":q" List.shtml
echo Done processing index.
findstr class=\"booktitle\" List.shtml > title
%myvim% -e -s -c ":s/^.*booktitle.>\s*\(.\{-}\)<.*/WSTITLE\1/g" -c ":wq" title
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

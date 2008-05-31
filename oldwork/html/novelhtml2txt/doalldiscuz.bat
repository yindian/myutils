@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt
for %%c in (tid*.html) do @(
    echo Processing %%c ...
    %myvim% -e -s -c ":so discuztid.vim" -c ":sav %%:r.txt" -c ":q" "%%c"
)
echo Done processing texts.
echo Processing index ...
type nul > index.txt
for %%c in (fid*.html) do @(
    echo Processing %%c ...
    grep "archiver/tid" %%c | sed "s/^.*archiver\/\(tid[^>]*\)\.html.>\([^<]*\)<.*/\1.txt \2/" >> index.txt
)
tac index.txt > index.txt.new
del index.txt
ren index.txt.new index.txt
echo Done processing index.
type nul > novel.txt
for /f "tokens=1*" %%c in (index.txt) do @(
    if exist %%c (
	echo filename=%%c   name=%%d
	echo WSSECTION%%d >> novel.txt
	type %%c >> novel.txt
    )
)

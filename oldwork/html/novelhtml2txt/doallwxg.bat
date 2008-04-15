@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
del *.txt
for %%c in (*.htm) do @(
    echo Processing %%c ...
    %myvim% -e -s -c ":so wenxinge.vim" -c ":sav %%:r.txt" -c ":q" "%%c"
)
echo Done processing texts.
del index.txt
echo Processing index ...
echo -e -s -c ":so wxgindex.vim" -c ":sav index.txt" -c ":q" index.htm
%myvim% -e -s -c ":so wxgindex.vim" -c ":sav index.txt" -c ":q" index.htm
echo Done processing index.
findstr class='max' index.htm > title
%myvim% -e -s -c ":s/^.*class='max'>\(.\{-}\)<.*/WSTITLE\1/g" -c ":wq" title
echo Done getting title.
rem type nul > novel.txt
type title > novel.txt
for /f "tokens=1*" %%c in (index.txt) do @(
	echo file=%%c section=%%d
	echo WSSECTION%%d >> novel.txt
	type %%c >> novel.txt
)

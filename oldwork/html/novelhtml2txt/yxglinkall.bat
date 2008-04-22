@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
:: assume \d\+\.txt already processed
:: assume index.txt already processed
:: assume title already processed
type title > novel.txt
set lastfile=
set title=
for /f "tokens=1*" %%c in (index.txt) do @(
    if "%%d"=="" (
        echo chapter=%%c
        echo WSCHAPTER%%c >> novel.txt
    ) else (
        if exist %%c (
            echo filename=%%c   name=%%d
            echo WSSECTION%%d >> novel.txt
            type %%c >> novel.txt
	    set lastfile=%%c
        ) else (
            echo chapter=%%c %%d
            echo WSCHAPTER%%c %%d >> novel.txt
        )
    )
)
echo Supplementary files
set lastfile=%lastfile:~,-4%.html
:loop
findstr /c:"var next_page" %lastfile% > tmp
rem %myvim% -e -s -c "s/^.*\"\(.*\)\".*/\1" -c ":wq" tmp
set /p lastfile=<tmp
set lastfile=%lastfile:~17,-2%
if "%lastfile%"=="index.html" goto end
findstr /c:"<div id=\"title\">" %lastfile% > tmp
set /p title=<tmp
echo filename=%lastfile:~,-5%.txt   name=%title:~16,-6%
echo WSSECTION%title:~16,-6% >> novel.txt
type %lastfile:~,-5%.txt >> novel.txt
goto loop
:end
echo Done.

@echo off
type nul > novel.txt
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

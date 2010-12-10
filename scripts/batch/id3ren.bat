@echo off
if "%1"=="" goto help
setlocal ENABLEDELAYEDEXPANSION
for %%c in (%1) do @(
set title=
for /f "tokens=2,3*" %%d in ('id3tool "%%c"') do @if "%%d"=="Title:" set title=%%e
echo ren "%%c" "%%~nc.!title!%%~xc"
ren "%%c" "%%~nc.!title!%%~xc"
)
goto end
:help
echo Usage: %0 file_name.mp3
echo Rename file_name.mp3 to file_name.song_title.mp3 according to ID3 tag
:end

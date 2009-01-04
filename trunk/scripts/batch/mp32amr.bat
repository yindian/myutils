@echo off
if "%1"=="" goto end
for %%c in (%1) do (
echo %%c
madplay -m -R 8000 -b 16 "%%c" -o "%%~nc.wav"
rem converter wav2amr "%%~nc.wav" "%%~nc.amr" MR795
amrnb-encoder MR795 "%%~nc.wav" "%%~nc.amr"
del "%%~nc.wav"
)

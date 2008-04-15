@echo off
if exist C:\progra~1\vim\vim64\vim.exe (
set myvim="C:\progra~1\vim\vim64\vim.exe"
) else set myvim=vim.exe
for %%c in (%1) do @(
  echo Processing %%c...
  %myvim% -e -s -c ":%%y" -c ":enew" -c ":pu" -c ":1d" -c ":sav! %%c" -c ":q" %%c
)

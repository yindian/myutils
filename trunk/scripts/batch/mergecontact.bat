@echo off
type nul > contact.out
echo Reading...
for %%c in (*.vcf) do @(
  echo "%%~nc">>contact.out
  type "%%c" | sed -n "4p" | sed "s/^[^:]*://;s/[A-Za-z]//g" >> contact.out
)
echo Merging...
rem type contact.out | tr -d \r | sed "N;s/\n/	/;s/:/ /g" > contact.txt
type contact.out | tr -d \r | sed "N;s/^.\(.*\).\n\(.*\)/s\/\2\/\1\//" > contact.sed
del contact.out

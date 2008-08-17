@echo off
set vmgs=*.vmg
if not "%1"=="" set vmgs="%1"
set outf=smslist.txt
if not "%2"=="" set outf="%2"
type nul > %outf%
for %%c in (%vmgs%) do @(
echo Processing %%c
type "%%c" | iconv -f utf-16le -t gb18030 -c | sed -n "9p;/^END:VBODY/q;13,$p" | sed -n "H;${g;s/^\nTEL:\(.*\)\nDate:\(\w*\).\(\w*\).\(\w*\)\([^\n]*\)/\4.\3.\2\5	\1	/;s/\n//;s/^\(....\.\)\(\w\)\./\10\2./;s/^\(....\.\w\w\.\)\(\w\) /\10\2 /;s/\n//g;p;}" >> %outf%
rem s/\\\\/\\\\\\\\/g;s/\n/\\\\n/g;
)
echo Sorting %outf%
usort %outf% > %outf%.out
type %outf%.out > %outf%
del %outf%.out
echo Done

1s/^document\.writeln("//
1s/")$//
%s/<p>/
%s/&nbsp;/ /g
%s/&quot;/"/g
%y
enew!
pu
1d
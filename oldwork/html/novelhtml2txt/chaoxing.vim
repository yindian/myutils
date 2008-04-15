1s/^document\.writeln("//
1s/")$//
%s/<p>//g
%s/&nbsp;/ /g
%s/&quot;/"/g
%y
enew!
pu
1d

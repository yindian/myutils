%s/<strong>\(.\{-}\)</
%s/href=.\{-}&id=\(\S\+\) title=\S\{-}>\([^<]*\)/
%s/^[^>].*$//
%s/^\n//
%s/\n$//
%s/^>//
%s/&nbsp;/ /g
%y
enew!
pu
1d
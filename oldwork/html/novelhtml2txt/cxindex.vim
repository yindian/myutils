%s/<strong>\(.\{-}\)</>\1/g
%s/href=.\{-}&id=\(\S\+\) title=\S\{-}>\([^<]*\)/>\1 \2/g
%s/^[^>].*$//
%s/^\n//
%s/\n$//
%s/^>//
%s/&nbsp;/ /g
%y
enew!
pu
1d

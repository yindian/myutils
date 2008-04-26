1s/\_.\{-}<div id="\=content[^>]*>\(\_.\{-}\)<script\_.*/\1/gi
%s/<\/\=div[^>]*>//g
%s/<[bh]r \/>//g
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/^\s*$\n//g
%s/\n^\s*$//g

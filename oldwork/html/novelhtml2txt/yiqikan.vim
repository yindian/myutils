set enc=utf-8
1s/^\_.\{-}<td [^>]*id="tcc">\(\_.\{-}\)<\/td>\_.*/\1/g
%s/<div style=.display:none.>.\{-}<\/div>//g
%s/<br\s\=\/\=>/
%s/<p>/
%s/
%s/^\s\+//
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/　/  /g
%s/•/·/g
%s/^\s*$\n//g
%s/\n^\s*$//g
set ff=dos
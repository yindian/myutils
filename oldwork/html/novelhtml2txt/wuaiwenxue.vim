1s/^\_.\{-}<div id="BookText">\(\_.\{-}\)<\(font\|script\)\_.*/\1/g
%s/<div style=.display:none.>.\{-}<\/div>//g
%s/<\/\=div[^>]*>//g
%s/<br\s\=\/\=>/
%s/<p>/
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/��/  /g
%s/^\s*$\n//g
%s/\n^\s*$//g
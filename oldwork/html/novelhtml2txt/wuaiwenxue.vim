1s/^\_.\{-}<div id="BookText">\(\_.\{-}\)<font style="display:none\_.*/\1/g
%s/<div style=.display:none.>.\{-}<\/div>//g
%s/<br\s\=\/\=>//g
%s/<p>//g
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/��/  /g
%s/^\s*$\n//g
%s/\n^\s*$//g

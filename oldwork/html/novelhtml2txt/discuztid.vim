1s/^\_.\{-}<div class="archiver_postbody">\(\_.\{-}\)<\/div\_.*/\1/g
%s/<span style=.display:none.>\_.\{-}<\/span>//g
%s/<font style=.font-size:0p[^>]*>\_.\{-}<\/font>//g
"%s/<\/\=div[^>]*>//g
%s/<h.>\([^<]*\)<\/h.>/
%s/<br\s\=\/\=>/
%s/<p>/
%s/
set ff=dos
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/��/  /g
%s/^\s*$\n//g
%s/\n^\s*$//g
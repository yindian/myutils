%s///g
1s/^\_.\{-}\(<div class=.archiver_post.>\_.\{-}\)<div class=.archiver_pages\_.*/\1/
%s/<span style=.display:none.>\_.\{-}<\/span>//g
%s/<font style=.font-size:0p[^>]*>\_.\{-}<\/font>//g
%s/<div class=.archiver_post.>/WSSUBSECTION/
%s/<cite>.*<\/p>//
%s/<\/\=div[^>]*>//g
%s/<h.>\([^<]*\)<\/h.>/\1/g
%s/<br\s\=\/\=>//g
%s/<p>//g
set ff=dos
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/¡¡/  /g
%s/^\s*$\n//g
%s/\n^\s*$//g
%s/\s\+$//
%s/^WSSUBSECTION\zs\n//

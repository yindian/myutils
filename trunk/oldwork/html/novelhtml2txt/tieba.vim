1s/^\_.\{-}\n\ze<font color=#0000cc>//
1s/^\(\_.*\n<td align=left.*\n\)\_.*/\1/
1s/^\(\_.\{-}\n<td align=left\s*>作者：\(.*\)<script.*\n\_.\{-}\n\)<cc>.*\n<\/.*\n<\/.*\n<t.*\n<t.*\n<td align=left\s*>作者：\2\@!.*\n\_.*/\1/
1s/<font[^>]*>\(.*\)<\/font.*/>WSSECTION\1/
%s/^<cc>/>/
%s/^[^>].*//
%s/^\n//
%s/\n$//
%s/^>//
%s/<\/cc>$//
%s///g
%s/<br>//g
%s/&amp;/\&/g
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/&lt;/</g
%s/&gt;/>/g
%s/　/  /g
%s/\s\+$//
%s/^\n\+//
"%s/^\s*/    /
"%s/^\s*WS/WS/

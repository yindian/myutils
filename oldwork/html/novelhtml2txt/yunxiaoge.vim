1s/\_.\{-}<div id="\=content"\=>\(\_.\{-}\)<\(\/div\|script\)\_.*/\1/gi
%s/<br \/>/
%s/&nbsp;/ /g
%s/&quot;/"/g
%s/^\s*$\n//g
%s/\n^\s*$//g
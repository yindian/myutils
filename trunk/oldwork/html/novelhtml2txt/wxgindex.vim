1s/\_.\{-}\(<a href='\d\{-}\.htm'>\)/\1/g
%s/<a href='\(\d\{-}\)\.htm'>\(.\{-}\)<\/a>/
%s/^[^1-9].*//g
%s/^\s*$\n//g
%s/\n^\s*$//g
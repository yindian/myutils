%s/^.*id="NclassTitle">\(.\{-}\)\(&nbsp;\)*\s\=[\[��]\s\=<.*$/>\1/
%s/^.*<li><a href="\(.*\)\.shtml\="\_.\{-}>\(.*\)<\/a>.*/>\1.txt \2/
%s/^[^>].*$//
%s/^$\n//
%s/\n^$//
%s/&nbsp;/ /g
%s/^>//
%s///

%s/^.*id="NclassTitle">\%(<h[^>]*>\)\=\(.\{-}\)\%(\%(&nbsp;\)*\s\=[\[��]\s\=\)\=<.*$/>\1/
%s/^.*<li><a href="\(.*\)\.shtml\="\_.\{-}>\_s*\(\_.\{-}\)\_s*<\/a>.*/>\1.txt \2/
%s/^[^>].*$//
%s/^$\n//
%s/\n^$//
%s/&nbsp;/ /g
%s/^>//
%s/
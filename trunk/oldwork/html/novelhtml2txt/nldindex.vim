e ++enc=utf-8
1s/\_.\{-}\n\(\s*<div class=.vol.>\_.\{-}\n\)\s*<div id=.copyright\_.*/\1/
%s/<div class=.vol.>\([^<]*\)<\/div>/
%s/<div class=.chapter.><a href=.\(\d\+\)\.htm[^>]*>\([^<]*\)</
%s/^[^>].*\n//
%s/^\n//
%s/\n$//
%s/^>//
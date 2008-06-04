e ++enc=utf-8
1s/\_.\{-}\n\(\s*<div class=.vol.>\_.\{-}\n\)\s*<div id=.copyright\_.*/\1/
%s/<div class=.vol.>\([^<]*\)<\/div>/>\1/
%s/<div class=.chapter.><a href=.\(\d\+\)\.htm[^>]*>\([^<]*\)</>\1.txt \2/
%s/^[^>].*\n//
%s/^\n//
%s/\n$//
%s/^>//

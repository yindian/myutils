set enc=utf-8
1s/^\_.\{-}<!--- r8artlbegin --->\(\_.\{-}\)<!--- \(nilongdao\|r8artlend\) --->\_.*/\1/
$s/逆龙道中文网(www.nilongdao.com)会员整理//
%s/<br\s\=\/\=>//gi
%s/<\/\=p>//gi
%s/<FONT style=.DISPLAY: none.>[^>]*>//gi
%s/&nbsp;/ /g
%s/　/  /g
%s/\s\+$//
%s/^\n//
-1s/\n$//
set ff=dos

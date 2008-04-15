function! WSFoldLevel(linenum)
	if getline(a:linenum) =~ '^WSCHAPTER.*'
		return '>1'
	elseif getline(a:linenum) =~ '^WSSECTION.*'
		return '>2'
	elseif getline(a:linenum) =~ '^WSSUBSECTION.*'
		return '>3'
	else
		return '='
	endif
endfunction

set foldexpr=WSFoldLevel(v:lnum)
set foldmethod=expr

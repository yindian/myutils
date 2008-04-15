function! WSFoldLevel(linenum)
	if getline(a:linenum) =~ '^CHAPTER.*'
		return '>1'
	elseif getline(a:linenum) =~ '^SECTION.*'
		return '>2'
	elseif getline(a:linenum) =~ '^SUBSECTION.*'
		return '>3'
	else
		return '='
	endif
endfunction

set foldexpr=WSFoldLevel(v:lnum)
set foldmethod=expr

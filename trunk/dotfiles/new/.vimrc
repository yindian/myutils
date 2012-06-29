" An example for a vimrc file.
"
" Maintainer:	Bram Moolenaar <Bram@vim.org>
" Last change:	2008 Dec 17
"
" To use it, copy it to
"     for Unix and OS/2:  ~/.vimrc
"	      for Amiga:  s:.vimrc
"  for MS-DOS and Win32:  $VIM\_vimrc
"	    for OpenVMS:  sys$login:.vimrc

" When started as "evim", evim.vim will already have done these settings.
if v:progname =~? "evim"
  finish
endif

" Use Vim settings, rather than Vi settings (much better!).
" This must be first, because it changes other options as a side effect.
set nocompatible

"""""""""""""""""""""""""""""""""""""""""""""
"	My adds
set noshellslash
"set path=.,c:/mingw/include,c:/mingw/include/c++/3.4.5,d:/usr/local/share/python/Lib,d:/usr/local/share/python/Lib/site-packages
set path=.,,/usr/include,/usr/lib/dbus-1.0/include,/usr/lib/gcc/i686-linux-gnu/4.4/include,/usr/lib/glib-2.0/include,/usr/lib/gtk-2.0/include,/usr/lib/jvm/java-6-openjdk/include,/usr/include/c++/4.4,/usr/local/include
set path+=/usr/include/apr-1.0,/home/okunch/prog/ServerFeibo/trunk/p2plib/client,/home/okunch/prog/ServerFeibo/trunk/p2plib/client/common
set path+=/usr/lib/python2.6,/usr/lib/python2.6/site-packages,/usr/lib/python2.6/dist-packages,/usr/local/lib/python2.6/site-packages,/usr/local/lib/python2.6/dist-packages,/usr/local/lib/python2.6/dist-packages/xmpppy-0.5.0rc1-py2.6.egg
abbr #i #include
abbr #d #define
set grepprg=grep\ -nH\ $*
set fo+=mM
set foldmethod=marker
set ww+=[,]
"set nowrap
set nostartofline
set selectmode=mouse,key
set keymodel=startsel
set showmatch
vmap <silent> <F2> "+y
nmap <silent> <F2> :up<cr>
imap <silent> <F2> <c-o>:up<cr>
vmap ,/ "zy/<C-R>=substitute(escape(@z, '[].*~/\\!'), '\n', '\\n', 'g')<CR><CR>
vmap ./ "zy/<C-R>/\\|<C-R>=substitute(escape(@z, '[].*~/\\!'), '\n', '\\n', 'g')<CR><CR>
nmap <silent> & "zyiw/<C-R>/\\|<C-R>=escape(@z, '[].*~/\\!')<CR><CR>
set ambw=single
set fencs=ucs-bom,utf-8,gb18030,cp932
"set fencs=cp936,utf-8,utf-16le,sjis,euc-jp
let g:fencview_autodetect = 0
set cino+=l1,t0,(0,w1,W2s,M1
"if &term != "gui"
"set bg=dark
"endif

nmap <silent> <F8> :Tlist<cr>

"""""""""""""""""""""""""""""""""""""""""""""
" allow backspacing over everything in insert mode
set backspace=indent,eol,start

"if has("vms")
"  set nobackup		" do not keep a backup file, use versions instead
"else
"  set backup		" keep a backup file
"endif
set history=50		" keep 50 lines of command line history
set ruler		" show the cursor position all the time
set showcmd		" display incomplete commands
set incsearch		" do incremental searching

" For Win32 GUI: remove 't' flag from 'guioptions': no tearoff menu entries
" let &guioptions = substitute(&guioptions, "t", "", "g")

" Don't use Ex mode, use Q for formatting
map Q gq

" CTRL-U in insert mode deletes a lot.  Use CTRL-G u to first break undo,
" so that you can undo CTRL-U after inserting a line break.
inoremap <C-U> <C-G>u<C-U>

" In many terminal emulators the mouse works just fine, thus enable it.
if has('mouse')
  set mouse=nv
endif

" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
if &t_Co > 2 || has("gui_running")
  syntax on
  set hlsearch
endif

" Only do this part when compiled with support for autocommands.
if has("autocmd")

  " Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
  filetype plugin indent on

  " Put these in an autocmd group, so that we can delete them easily.
  augroup vimrcEx
  au!

  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78

  " When editing a file, always jump to the last known cursor position.
  " Don't do it when the position is invalid or when inside an event handler
  " (happens when dropping a file on gvim).
  " Also don't do it when the mark is in the first line, that is the default
  " position when opening a file.
  autocmd BufReadPost *
    \ if line("'\"") > 1 && line("'\"") <= line("$") |
    \   exe "normal! g`\"" |
    \ endif

  augroup END

"""""""""""""""""""""""""""""""""""""""""""""
  autocmd BufRead,BufNewFile *.uml		set syntax=plantuml
  "autocmd BufRead,BufNewFile *.i		set isk< | set ft=c
  autocmd FileType cfg set suffixesadd=.cfg
  autocmd FileType c,cpp setlocal ts=4 | set sw=4 | set et | 
			  \ set tw=80 | compiler gcc
  autocmd FileType make if exists("loaded_matchit") |
			  \ let b:match_words = '^ *\<if\w*\>:^ *\<else\>:^ *\<endif\>' |
			  \ end
		
  if has("cscope")
      set nocsverb
      if $CSCOPE_DB != ""
          cs add $CSCOPE_DB
	  let g:CScopeOut=$CSCOPE_DB
      elseif filereadable("cscope.out")
          cs kill 0
          cs add ./cscope.out . 
	  let g:CScopeOut="./cscope.out"
      else
	  let g:CScopeOut=findfile("cscope.out", ".;")
	  if g:CScopeOut != ""
		  exe "cs add" g:CScopeOut strpart(g:CScopeOut, 0, match(g:CScopeOut, "/cscope.out$"))
	  endif
      endif
      set csverb
      set cst
      if filereadable(substitute(g:CScopeOut, "out$", "path", ""))
	      exec "source " . substitute(g:CScopeOut, "out$", "path", "")
      else
	      "echo "Warning: " . substitute(g:CScopeOut, "out$", "path", "") . " not readable"
      endif
      nmap <C-_> :cs find 3 <C-R>=expand("<cword>")<CR><CR>
      "nmap g<C-]> :cstag <C-R>=expand("<cword>")<CR><CR>
      nmap g<C-]> :scs find 0 <C-R>=expand("<cword>")<CR><CR>
      nmap g<C-\> :cs find 0 <C-R>=expand("<cword>")<CR><CR>
      vmap g<C-\> "zy:cs find s <C-R>z<CR>
      vmap g<C-]> "zy:scs find 4 <C-R>z<CR>
      vmap gF "zy:cs find f <C-R>z<CR>
      vmap g\ "zy:cs find g <C-R>z<CR>
      function! Myadd_csup(findpath)
	      if g:CScopeOut == ""
		      return
	      endif
	      if cscope_connection(4, g:CScopeOut, substitute(g:CScopeOut, "/[^/]*$", "", "")) || cscope_connection(4, g:CScopeOut)
		      exec "cs kill " . g:CScopeOut
		      if a:findpath == ""
			      if exists('g:findpath') && g:findpath != ""
				      let s:findpath = g:findpath
			      else
				      let s:findpath = substitute(g:CScopeOut, "/[^/]*$", "", "")
			      endif
		      else
			      let s:findpath = a:findpath
		      endif
		      let s:temp=system("make --no-print-directory -C " . s:findpath . " cscope")
		      echo s:temp
		      exec "cs add " . g:CScopeOut . " " . substitute(g:CScopeOut, "/[^/]*$", "", "")
	      else
		      echo "Cscope update failed"
	      endif
      endfunction
      command! Upcs call Myadd_csup("")
  endif
"""""""""""""""""""""""""""""""""""""""""""""
else

  set autoindent		" always set autoindenting on

endif " has("autocmd")

" Convenient command to see the difference between the current buffer and the
" file it was loaded from, thus the changes you made.
" Only define it when not defined already.
if !exists(":DiffOrig")
  command DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis
		  \ | wincmd p | diffthis
endif

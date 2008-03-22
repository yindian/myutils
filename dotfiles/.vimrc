" An example for a vimrc file.
"
" Maintainer:	Bram Moolenaar <Bram@vim.org>
" Last change:	2006 Nov 16
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

" Use Vim settings, rather then Vi settings (much better!).
" This must be first, because it changes other options as a side effect.
set nocompatible

" user specific settings
set fo+=mM
set fencs=cp936,utf-8,ucs-bom
set ambw=double
set nosol
set vb
set path+=/usr/include/c++/4.1.3/
set path+=/usr/local/include/
set ls=2
set statusline=%<%f%h%m%r%{'['.(&fenc!=''?&fenc:&enc).':'.&ff.']'}\ \ %b\ 0x%B%=\ %l,%c%V\ %P
abbr #i #include
abbr #d #define
if $TERM=~'^screen'
   :set ttymouse=xterm
endif 
vmap <unique> <silent> <leader>m :SelectionHighlighter<cr>
nmap <unique> <silent> <leader>c :ClearCurrentHighlighter<cr>
vnoremap <silent> ,/ y/<C-R>=escape(@", '\\/.*$^~[]')<CR><CR>
vnoremap <silent> ,? y?<C-R>=escape(@", '\\/.*$^~[]')<CR><CR>
nmap <C-F12> :!ctags -R --c++-kinds=+p --fields=+iaS --extra=+q .<CR>
imap <unique> <silent> <F2> <c-o>:up<cr>
let g:fencview_autodetect = 0
autocmd FileType tex set isk+=64-64| imap <F3> <C-v>~<C-v>~<++><Esc>4hi| imap <F2> <C-v>~| imap <F4> <C-v>~<C-v>\|<C-v>\|<C-v>~<++><Esc>5hi| imap <F6> <C-v>\||
\let g:Tex_ViewRule_pdf = 'evince'|
\let g:Tex_MultipleCompileFormats = 'dvi,ps,pdf'|
\imap <F2> <c-o>:up<cr>|
\nmap <silent> <Leader>lt :let mytemp = g:Tex_CompileRule_dvi<cr>:let g:Tex_CompileRule_dvi = 'etex -interaction=nonstopmode -src-specials $*'<cr>:let mytemp2 = g:Tex_CompileRule_pdf<cr>:let g:Tex_CompileRule_pdf = 'pdftex -interaction=nonstopmode -src-specials $*'<cr>:call Tex_RunLaTeX()<cr>:let g:Tex_CompileRule_dvi = mytemp<cr>:let g:Tex_CompileRule_pdf = mytemp2<cr>|
\nmap <silent> <Leader>lx :TTarget pdf<cr>:let mytemp = g:Tex_CompileRule_pdf<cr>:let g:Tex_CompileRule_pdf = 'xetex -interaction=nonstopmode $*'<cr>:call Tex_RunLaTeX()<cr>:let g:Tex_CompileRule_pdf = mytemp<cr>|
\nmap <silent> <Leader>le :TTarget pdf<cr>:let mytemp = g:Tex_CompileRule_pdf<cr>:let g:Tex_CompileRule_pdf = 'xelatex -interaction=nonstopmode $*'<cr>:call Tex_RunLaTeX()<cr>:let g:Tex_CompileRule_pdf = mytemp<cr>|
let g:tex_flavor="tex"
autocmd FileType cpp set sw=4| set ts=4
" end user specific
" allow backspacing over everything in insert mode
set backspace=indent,eol,start

if has("vms")
  set nobackup		" do not keep a backup file, use versions instead
else
  set backup		" keep a backup file
endif
set history=50		" keep 50 lines of command line history
set ruler		" show the cursor position all the time
set showcmd		" display incomplete commands
set incsearch		" do incremental searching

" For Win32 GUI: remove 't' flag from 'guioptions': no tearoff menu entries
" let &guioptions = substitute(&guioptions, "t", "", "g")

" Don't use Ex mode, use Q for formatting
map Q gq

" In many terminal emulators the mouse works just fine, thus enable it.
set mouse=a

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
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal! g`\"" |
    \ endif

  augroup END

else

  set autoindent		" always set autoindenting on

endif " has("autocmd")

" Convenient command to see the difference between the current buffer and the
" file it was loaded from, thus the changes you made.
command DiffOrig vert new | set bt=nofile | r # | 0d_ | diffthis
	 	\ | wincmd p | diffthis

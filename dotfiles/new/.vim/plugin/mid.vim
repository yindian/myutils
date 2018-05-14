" Vim plugin for editing midi files.

" Exit quickly when:
" - this plugin was already loaded
" - when 'compatible' is set
" - some autocommands are already taking care of compressed files
if exists("loaded_midi") || &cp || exists("#BufReadPre#*.mid")
  finish
endif
let loaded_midi = 1

augroup midi
  " Remove all midi autocommands
  au!

  " Enable editing of midi files.
  "
  " Set binary mode before reading the file.
  au BufReadPre 	*.mid,*.midi setlocal bin
  au BufReadPost	*.mid,*.midi silent %!mf2t
  au BufReadPost	*.mid,*.midi setlocal eol
  au BufWritePre	*.mid,*.midi let b:curpos = getcurpos()
  au BufWritePre	*.mid,*.midi silent %!t2mf
  au BufWritePre	*.mid,*.midi setlocal noeol
  au BufWritePost	*.mid,*.midi silent %!mf2t
  au BufWritePost	*.mid,*.midi setlocal eol nomod | diffu
  au BufWritePost	*.mid,*.midi call setpos('.', b:curpos)
augroup END

" To textify midi files in Git, add the following line to the repo's .gitattributes:
" *.mid binary diff=mid
"
" And then config the repo as:
" diff.mid.textconv=mf2t
" diff.mid.binary=true

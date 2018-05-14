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
  au BufReadPost	*.mid,*.midi call s:mf2t()
  au BufWritePost	*.mid,*.midi call s:t2mf()
  au FileChangedShell	*.mid,*.midi silent
augroup END

fun s:mf2t()
  let tmp = tempname()
  exe "silent w " . fnameescape(tmp) . ".mid"
  call system("mf2t " . shellescape(tmp) . ".mid " . shellescape(tmp))
  if !v:shell_error && filereadable(tmp)
    %d _
    setlocal nobin
    exe "silent 0r ++edit " . tmp
    silent $d _
    1
    call delete(tmp)
    call delete(tmp . ".mid")
    silent! exe "bwipe " . fnameescape(tmp)
    silent! exe "bwipe " . fnameescape(tmp) . ".mid"
    let b:mf2tOk = 1
  else
    let b:mf2tOk = 0
    echoerr "Error: mf2t failed"
  endif
endfun

fun s:t2mf()
  if b:mf2tOk
    let tmp = tempname()
    let fn = resolve(expand("<afile>"))
    if rename(fn, tmp) == 0
      call system("t2mf " . shellescape(tmp) . " " . shellescape(fn))
      if v:shell_error
        call rename(tmp, fn)
        echoerr "Error: t2mf failed"
      else
        call delete(tmp)
      endif
    endif
  else
    echomsg "Not textified midi"
  endif
endfun

" To textify midi files in Git, add the following line to the repo's .gitattributes:
" *.mid binary diff=mid
"
" And then config the repo as:
" diff.mid.textconv=mf2t
" diff.mid.binary=true

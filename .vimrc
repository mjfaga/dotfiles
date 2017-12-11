set nocompatible

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

Plugin 'gmarik/Vundle.vim'
Plugin 'w0ng/vim-hybrid'
Plugin 'avakhov/vim-yaml'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
Plugin 'christoomey/vim-tmux-navigator'
Plugin 'godlygeek/tabular'
Plugin 'groenewege/vim-less'
Plugin 'Lokaltog/vim-easymotion'
Plugin 'haya14busa/incsearch.vim'
Plugin 'haya14busa/incsearch-easymotion.vim'
Plugin 'prettier/vim-prettier', {
  \ 'do': 'yarn install',
  \ 'for': ['javascript', 'typescript', 'css', 'less', 'scss', 'json', 'graphql', 'markdown'] }
Plugin 'Yggdroot/indentLine'
Plugin 'othree/html5.vim'
Plugin 'pangloss/vim-javascript'
Plugin 'mxw/vim-jsx'
Plugin 'scrooloose/nerdcommenter'
Plugin 'scrooloose/nerdtree'
" Plugin 'scrooloose/syntastic'
Plugin 'w0rp/ale'
Plugin 'keith/rspec.vim'
Plugin 'Xuyuanp/nerdtree-git-plugin'
Plugin 'tpope/vim-abolish'
Plugin 'tpope/vim-endwise'
Plugin 'tpope/vim-repeat'
Plugin 'tpope/vim-surround'
Plugin 'tpope/vim-fugitive'
Plugin 'tpope/vim-rails'
Plugin 'tpope/vim-bundler'
Plugin 'tpope/vim-dispatch'
Plugin 'alvan/vim-closetag'
Plugin 'jiangmiao/auto-pairs'
" Plugin 'tpope/vim-rake'
Plugin 'vim-ruby/vim-ruby'
Plugin 'janko-m/vim-test'
Plugin 'slim-template/vim-slim.git'
Plugin 'andrewradev/splitjoin.vim'
" Plugin 'gcmt/taboo.vim'
" Plugin 'ngmy/vim-rubocop'
" Plugin 'vim-scripts/gitignore'
Plugin 'kana/vim-textobj-user'
Plugin 'nelstrom/vim-textobj-rubyblock'
Plugin 'prabirshrestha/async.vim'               " Async.vim - Normalized interface to Vim 8 & NeoVim async jobs
Plugin 'junegunn/fzf'
Plugin 'junegunn/fzf.vim'
Plugin 'jparise/vim-graphql'
Plugin 'hail2u/vim-css3-syntax'
Plugin 'ap/vim-css-color'

" All of your Plugins must be added before the following line
call vundle#end()            " required

" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal

let mapleader = ","

cabbrev W w
cabbrev Q q
cabbrev Wq wq

" GLOBAL MAPPINGS
noremap \ :NERDTreeToggle<CR>
noremap \| :NERDTreeFind<CR>

" NORMAL MAPINGS
nnoremap - ddp                                                                                    " Move line down
nnoremap _ dd1kP                                                                                  " Move line up
nnoremap <leader>ev :vsplit $MYVIMRC<cr>                                                          " Edit ~/.vimrc file
nnoremap <leader>sv :source $MYVIMRC<cr>                                                          " Source ~/vimrc file
nnoremap <leader>" viw<esc>a"<esc>bi"<esc>lel                                                     " Quote the selected word

" INSERT MAPPINGS
inoremap <c-d> <esc>ddi                                                                           " Delete line while in insert mode
inoremap <c-u> <esc>viwUi                                                                         " Uppercase current word in insert mode
inoremap jk <esc>                                                                                 " New escape key (<esc>, <c-c>, <c-[>)

" OPERATION MAPPINGS
onoremap an{ :<c-u>normal! f(va{<cr>
onoremap al{ :<c-u>normal! F(va{<cr>
onoremap in{ :<c-u>normal! f(vi{<cr>
onoremap il{ :<c-u>normal! F(vi{<cr>
onoremap an( :<c-u>normal! f(va(<cr>
onoremap al( :<c-u>normal! F(va(<cr>
onoremap in( :<c-u>normal! f(vi(<cr>
onoremap il( :<c-u>normal! F(vi(<cr>

" PLUGIN MAPPINGS
" haya14busa/incsearch.vim - basic overrides
map /  <Plug>(incsearch-forward)
map ?  <Plug>(incsearch-backward)
map g/ <Plug>(incsearch-stay)

" haya14busa/incsearch.vim - no highlight overrides
let g:incsearch#auto_nohlsearch = 1
map n  <Plug>(incsearch-nohl-n)
map N  <Plug>(incsearch-nohl-N)
map *  <Plug>(incsearch-nohl-*)
map #  <Plug>(incsearch-nohl-#)
map g* <Plug>(incsearch-nohl-g*)
map g# <Plug>(incsearch-nohl-g#)

" haya14busa/incsearch-easymotion.vim - all buffer easymotion searches
map <Leader><Leader>l <Plug>(easymotion-bd-jk)
nmap <Leader><Leader>l <Plug>(easymotion-overwin-line)

function! s:incsearch_config(...) abort
  return incsearch#util#deepextend(deepcopy({
  \   'modules': [incsearch#config#easymotion#module({'overwin': 1})],
  \   'keymap': {
  \     "\<CR>": '<Over>(easymotion)'
  \   },
  \   'is_expr': 0
  \ }), get(a:, 1, {}))
endfunction

noremap <silent><expr> z/  incsearch#go(<SID>incsearch_config())
noremap <silent><expr> z?  incsearch#go(<SID>incsearch_config({'command': '?'}))
noremap <silent><expr> zg/ incsearch#go(<SID>incsearch_config({'is_stay': 1}))

" VIM SETTINGS
syntax on                                                                                         " Enable syntax highlighting
filetype on                                                                                       " Enable filetype detection
filetype indent on                                                                                " Enable filetype-specific indenting
filetype plugin on                                                                                " Enable filetype-specific plugins

set hlsearch
set number                                                                                        " Line numbers
set relativenumber                                                                                " Show relative line numbers
set nowrap                                                                                        " No wrapping
set tabstop=2                                                                                     " Make tabs as wide as two spaces
set softtabstop=2                                                                                 " Support deleting spaces in sets of two spaces
set autoindent                                                                                    " Be smart about indentations
set expandtab                                                                                     " Convert tabs to spaces
set smarttab                                                                                      " Use shiftwidth to tab at line beginning
set shiftwidth=2                                                                                  " Width of autoindent
set shiftround                                                                                    " Round shift to nearest shiftwidth
set list                                                                                          " Show whitespace
set listchars=trail:·
set showmatch                                                                                     " Show matching brackets
set splitright                                                                                    " Add new windows towards the right
set splitbelow                                                                                    " ... and bottom
set backspace=indent,eol,start                                                                    " Let backspace work over anything.
set lcs=tab:▸\ ,trail:·,eol:¬,nbsp:_                                                              " Show “invisible” characters
set clipboard=unnamed                                                                             " Use the OS clipboard by default (on versions compiled with `+clipboard`)
"set wildmenu                                                                                      " Enhance command-line completion
"set esckeys                                                                                       " Allow cursor keys in insert mode
"set backspace=indent,eol,start                                                                    " Allow backspace in insert mode
"set ttyfast                                                                                       " Optimize for fast terminal connections
set gdefault                                                                                      " Add the g flag to search/replace by default
"set encoding=utf-8 nobomb                                                                         " Use UTF-8 without BOM
"set binary
"set noeol                                                                                         " Don’t add empty newlines at the end of files
set backupdir=~/.vim/backups                                                                      " Centralize backups
set directory=~/.vim/swaps                                                                        " Centralize swaps
if exists("&undodir")
  set undodir=~/.vim/undo                                                                         " Centralize undo commands
endif
set backupskip=/tmp/*,/private/tmp/*                                                              " Don’t create backups when editing files in certain directories
"set modeline                                                                                      " Respect modeline in files
"set modelines=4
set exrc                                                                                          " Enable per-directory .vimrc files and disable unsafe commands in them
"set secure
"set list
set ignorecase                                                                                    " Ignore case of searches
set incsearch                                                                                     " Highlight dynamically as pattern is typed
set laststatus=2                                                                                  " Always show status line
set statusline=%<%f\ %y%h%m%r%=%b\ 0x%B\ \ %l,%c%V\ %P                                            " Custom status line format
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*
set statusline+=%{fugitive#statusline()}
set mouse=a                                                                                       " Enable mouse in all modes
set noerrorbells                                                                                  " Disable error bells
"set nostartofline                                                                                 " Don’t reset cursor to start of line when moving around.
set ruler                                                                                         " Show the cursor position
"set shortmess=atI                                                                                 " Don’t show the intro message when starting Vim
set showmode                                                                                      " Show the current mode
set title                                                                                         " Show the filename in the window titlebar
set showcmd                                                                                       " Show the (partial) command as it’s being typed
set scrolloff=3                                                                                   " Start scrolling three lines before the horizontal window border
set cursorline                          " Highlight current line

" THEME
set background=dark
" let g:hybrid_custom_term_colors = 1
" let g:hybrid_reduced_contrast = 1
colorscheme hybrid
hi rubyDefine ctermfg=166
" hi rubySymbol ctermfg=125
let &colorcolumn="81," . join(range(121,999),",")

" Indentation Guides
let g:indentLine_setColors = 1
let g:indentLine_char = '│'

"" COPY/PASTE
"vmap <Leader>y "+y
"vmap <Leader>d "+d
"nmap <Leader>p "+p
"nmap <Leader>P "+P
"vmap <Leader>p "+p
"vmap <Leader>P "+P

"" SPLIT NAVIGATION
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

"" TAB NAVIGATION
nnoremap <C-Left> :tabprevious<CR>
nnoremap <C-Right> :tabnext<CR>
nnoremap <silent> <A-Left> :execute 'silent! tabmove ' . (tabpagenr()-2)<CR>
nnoremap <silent> <A-Right> :execute 'silent! tabmove ' . tabpagenr()<CR>

"nmap <leader>T :enew<cr>                " To open a new empty buffer; replaces :tabnew
"nmap <leader>l :bnext<CR>               " Move to the next buffer
"nmap <leader>h :bprevious<CR>           " Move to the previous buffer
"nmap <leader>bq :bp <BAR> bd #<CR>      " Close current buffer and move to previous one, replicates idea of closing tab
"nmap <leader>bl :ls<CR>                 " Show all open buffers and their status
"map q: :q                               " stop annoying window from popping up
nnoremap <Leader>w :w<CR>

" Nerd commenter defaults
let g:NERDSpaceDelims = 1
let g:NERDDefaultAlign = 'left'
let g:NERDCommentEmptyLines = 1
let g:NERDTrimTrailingWhitespace = 1

" Saner NERDTree Mappings/Deferts
let g:NERDTreeMapOpenSplit='s'
let g:NERDTreeMapPreviewSplit='gs'
let g:NERDTreeMapOpenVSplit='v'
let g:NERDTreeMapPreviewVSplit='gv'
let g:NERDTreeShowHidden = 1
let g:NERDTreeHighlightCursorline = 1
let g:NERDTreeMinimalUI = 1
let g:NERDTreeAutoDeleteBuffer = 1
let g:NERDTreeWinSize = 51

" Toolbar colors
:let g:airline_theme='sol'
:let g:airline#extensions#tabline#enabled = 1
:let g:airline#extensions#tabline#fnamemod = ':t'

" vim-test
nmap <silent> <leader>t :TestNearest<CR>
nmap <silent> <leader>T :TestFile<CR>
nmap <silent> <leader>a :TestSuite<CR>
nmap <silent> <leader>l :TestLast<CR>
nmap <silent> <leader>g :TestVisit<CR>
let test#strategy = "dispatch_background"

runtime macros/matchit.vim " WHAT IS THIS?

let g:jsx_ext_required = 0 " Allow JSX in normal JS files

" w0rp/ae configurations
" https://github.com/w0rp/ale#5xii-how-can-i-check-jsx-files-with-both-stylelint-and-eslint
augroup FiletypeGroup
    autocmd!
    au BufNewFile,BufRead *.jsx set filetype=javascript.jsx
augroup END

let g:ale_linters = {'jsx': ['stylelint', 'eslint']}
let g:ale_linter_aliases = {'jsx': 'css'}

" Syntastic configurations
" let g:syntastic_javascript_checkers = ['eslint']
" let g:syntastic_check_on_open = 1
" let g:syntastic_check_on_wq = 0

" vim-css3-syntax
augroup VimCSS3Syntax
  autocmd!

  autocmd FileType css setlocal iskeyword+=-
augroup END

" vim-closetag configurations
let g:closetag_filenames = '*.html,*.xhtml,*.phtml,*.html.erb,*.html.slim'
let g:closetag_xhtml_filenames = '*.xhtml,*.jsx,*html.erb,*.html.slim'

" Automatically open nerd tree when vim started without a file specified
" autocmd StdinReadPre * let s:std_in=1
" autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif

" Automatically close vim when only nerd tree is left open
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" Treat .json files as .js
autocmd BufNewFile,BufRead *.json setfiletype json syntax=javascript

" Treat .md files as Markdown
autocmd BufNewFile,BufRead *.md setlocal filetype=markdown

" Strip trailing whitespace when saving files
function! StripTrailingWhitespace()
  let save_cursor = getpos(".")
  %s/\s\+$//e
  call setpos('.', save_cursor)
endfunction
augroup presave
  autocmd!
  autocmd BufWritePre *.* call StripTrailingWhitespace()
augroup END
noremap <leader>ss :call StripTrailingWhitespace()<CR>

" Automatically reindent files before save
" :autocmd BufWritePre *.html :normal gg=G

" Create directories that don't exist when saving a file
function! s:MkNonExDir(file, buf)
  if empty(getbufvar(a:buf, '&buftype')) && a:file!~#'\v^\w+\:\/'
    let dir=fnamemodify(a:file, ':h')
    if !isdirectory(dir)
      call mkdir(dir, 'p')
    endif
  endif
endfunction
augroup BWCCreateDir
  autocmd!
  autocmd BufWritePre * :call s:MkNonExDir(expand('<afile>'), +expand('<abuf>'))
augroup END

" Show which highlight groups apply to the item under the cursor
" https://jordanelver.co.uk/blog/2015/05/27/working-with-vim-colorschemes/
nmap <leader>sp :call <SID>SynStack()<CR>
function! <SID>SynStack()
  if !exists("*synstack")
    return
  endif
  echo map(synstack(line('.'), col('.')), 'synIDattr(v:val, "name")')
endfunc

let g:prettier#autoformat = 0
autocmd BufWritePre *.js,*.jsx,*.mjs,*.ts,*.tsx,*.css,*.less,*.scss,*.json,*.graphql PrettierAsync
autocmd FileType javascript set formatprg=prettier-eslint\ --stdin

" FZF
nnoremap <leader>f :FZF!<cr>
nnoremap <leader>e :Find!<cr>
nnoremap <leader>c :FindCursor!<cr>
command! -bang -nargs=* Find call fzf#vim#grep('rg --column --line-number --no-heading --color "always" '.shellescape(<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)
command! -bang -nargs=* FindCursor call fzf#vim#grep('rg --column --line-number --no-heading --color "always" '.shellescape(empty(<q-args>)?expand("<cword>"):<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)

" CTAGS via Async
" function! s:CtagsAsync()
"   let job_id = async#job#start(['atomic-ctags'],
"         \ {
"         \   'on_exit': function('s:on_exit'),
"         \ })
" endfunction
" command! CtagsAsync call <sid>CtagsAsync()
"
" function! s:on_exit(job_id, exit_code, _)
"   if a:exit_code != 0
"     echohl Error
"     echom 'Error running: ' . a:job_id . '; exit code: ' . a:exit_code
"     echohl None
"   endif
" endfunction
"
" augroup async_ctags
"   autocmd!
"   autocmd VimEnter * CtagsAsync
"   autocmd BufWritePost * CtagsAsync
" augroup END
"
" " vim:ft=vim

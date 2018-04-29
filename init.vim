set nocompatible

" set the runtime path to include Plugged and initialize
call plug#begin('~/.vim/plugged')

" Search
Plug 'mileszs/ack.vim'

" Tabs
Plug 'vim-scripts/Tabmerge'

Plug 'djoshea/vim-autoread'
Plug 'w0ng/vim-hybrid'
Plug 'avakhov/vim-yaml'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'christoomey/vim-tmux-navigator'
Plug 'godlygeek/tabular'
Plug 'groenewege/vim-less'
Plug 'Lokaltog/vim-easymotion'
Plug 'haya14busa/incsearch.vim'
Plug 'haya14busa/incsearch-easymotion.vim'
Plug 'prettier/vim-prettier', {
  \ 'do': 'yarn install',
  \ 'for': ['javascript', 'typescript', 'css', 'less', 'scss', 'json', 'graphql', 'markdown'] }
Plug 'Yggdroot/indentLine'
Plug 'othree/html5.vim'
Plug 'pangloss/vim-javascript'
Plug 'mxw/vim-jsx'
Plug 'scrooloose/nerdcommenter'
Plug 'scrooloose/nerdtree'
" Plug 'scrooloose/syntastic'
Plug 'w0rp/ale'
Plug 'keith/rspec.vim'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'tpope/vim-abolish'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-repeat'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-rails'
Plug 'tpope/vim-bundler'
Plug 'tpope/vim-dispatch'
Plug 'alvan/vim-closetag'
Plug 'jiangmiao/auto-pairs'
" Plug 'tpope/vim-rake'
Plug 'vim-ruby/vim-ruby'
Plug 'janko-m/vim-test'
Plug 'slim-template/vim-slim'
Plug 'andrewradev/splitjoin.vim'
" Plug 'gcmt/taboo.vim'
" Plug 'ngmy/vim-rubocop'
" Plug 'vim-scripts/gitignore'
Plug 'kana/vim-textobj-user'
Plug 'nelstrom/vim-textobj-rubyblock'
Plug 'prabirshrestha/async.vim'               " Async.vim - Normalized interface to Vim 8 & NeoVim async jobs
Plug 'junegunn/fzf'
Plug 'junegunn/fzf.vim'
Plug 'jparise/vim-graphql'
Plug 'hail2u/vim-css3-syntax'
Plug 'ap/vim-css-color'
Plug 'styled-components/vim-styled-components'
Plug 'leafgarland/typescript-vim'
Plug 'mattn/emmet-vim'
Plug 'machakann/vim-highlightedyank'
if has('nvim')
  Plug 'kassio/neoterm'
endif

" All of your Plugins must be added before the following line
call plug#end()            " required

" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal

" NeoVim Terminal
if has('nvim')
  " Escape to exit terminal mode
  :tnoremap <Esc> <C-\><C-n>

  " Restore navigation between terminal windows/vim windows
  :tnoremap <A-h> <C-\><C-N><C-w>h
  :tnoremap <A-j> <C-\><C-N><C-w>j
  :tnoremap <A-k> <C-\><C-N><C-w>k
  :tnoremap <A-l> <C-\><C-N><C-w>l

  " Paste registers into terminal with alt-r
  :tnoremap <expr> <A-r> '<C-\><C-n>"'.nr2char(getchar()).'pi'
endif
:inoremap <A-h> <C-\><C-N><C-w>h
:inoremap <A-j> <C-\><C-N><C-w>j
:inoremap <A-k> <C-\><C-N><C-w>k
:inoremap <A-l> <C-\><C-N><C-w>l
:nnoremap <A-h> <C-w>h
:nnoremap <A-j> <C-w>j
:nnoremap <A-k> <C-w>k
:nnoremap <A-l> <C-w>l

" Ack
let g:ackprg = 'rg --hidden --vimgrep'

let mapleader = ","

cabbrev W w
cabbrev Q q
cabbrev Wq wq

" GLOBAL MAPPINGS
noremap \ :NERDTreeToggle<CR>
noremap \| :NERDTreeFind<CR>

" NORMAL MAPINGS
" When lines are wrapped, always navigate 1 up/down
nnoremap j gj
nnoremap k gk

" Move line down
nnoremap - ddp
" Move line up
nnoremap _ dd1kP
" Edit ~/.vimrc file
nnoremap <leader>ev :vsplit $MYVIMRC<cr>
" Source ~/vimrc file
nnoremap <leader>sv :source $MYVIMRC<cr>
" Quote the selected word
nnoremap <leader>" viw<esc>a"<esc>bi"<esc>lel

" INSERT MAPPINGS
" Delete line while in insert mode
inoremap <c-d> <esc>ddi
" Uppercase current word in insert mode
inoremap <c-u> <esc>viwUi
" New escape key (<esc>, <c-c>, <c-[>)
inoremap jk <esc>
"
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
if has('autocmd')
  filetype plugin indent on                                                                       " Enable filetype detection, filetype-specific indenting/plugins
endif
if has('syntax') && !exists('g:syntax_on')
  syntax enable                                                                                   " Enable syntax highlighting
endif

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
set listchars=tab:>\ ,trail:-,extends:>,precedes:<,nbsp:+
set formatoptions+=j                                                                              " Delete comment character when joining commented lines
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
set encoding=utf-8                                                                               " Use UTF-8
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
set incsearch                                                                                     " Highlight dynamically as pattern is typed
set hlsearch                                                                                      " Highlight all matches when search accepted
set ignorecase                                                                                    " Ignore case of searches
set smartcase                                                                                     " If capital letter typed, make search case sensitive
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
set sidescrolloff=5
set display+=lastline
set cursorline                          " Highlight current line
set shell=/bin/bash
" Neovim options
if has('nvim')
  set inccommand=split                          " Live highlight of interactive commands like substitute
endif

" THEME
set background=dark
" let g:hybrid_custom_term_colors = 1
" let g:hybrid_reduced_contrast = 1
colorscheme hybrid
hi rubyDefine ctermfg=166
" hi rubySymbol ctermfg=125
let &colorcolumn="81," . join(range(121,999),",")
if has('nvim')
  " Highlight cursor in terminal mode even when terminal not active
  hi! TermCursorNC ctermfg=15 guifg=#fdf6e3 ctermbg=14 guibg=#93a1a1 cterm=NONE gui=NONE
endif


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


"" TAB NAVIGATION
nnoremap <C-Left> :tabprevious<CR>
nnoremap <C-Right> :tabnext<CR>
nnoremap <silent> <A-Left> :execute 'silent! tabmove ' . (tabpagenr()-2)<CR>
nnoremap <silent> <A-Right> :execute 'silent! tabmove ' . tabpagenr()<CR>

"nmap <leader>T :enew<cr>                " To open a new empty buffer; replaces :tabnew
nmap <leader>l :bnext<CR>               " Move to the next buffer
nmap <leader>h :bprevious<CR>           " Move to the previous buffer
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
nmap <silent> <leader>L :TestLast<CR>
nmap <silent> <leader>g :TestVisit<CR>
if has('nvim')
  let test#strategy = "neoterm"
else
  let test#strategy = "dispatch"
endif

" Load matchit.vim, but only if the user hasn't installed a newer version.
if !exists('g:loaded_matchit') && findfile('plugin/matchit.vim', &rtp) ==# ''
  runtime! macros/matchit.vim
endif

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
command! -bang -nargs=* Find call fzf#vim#grep('rg --column --line-number --color "always" '.shellescape(<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)
command! -bang -nargs=* FindCursor call fzf#vim#grep('rg --column --line-number --no-heading --color "always" '.shellescape(empty(<q-args>)?expand("<cword>"):<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)
" Neovim - Esc to close FZF window
if has('nvim')
  autocmd FileType fzf tnoremap <buffer> <ESC> <C-c>
endif

" Tabmerge
nnoremap <leader>tm :execute "Tabmerge left"<cr>

function! ExtractUrlFromCurrentLine()
  return matchstr(getline("."), "http[^ ]*")
endfunction
command! OpenUrlOnCurrentLineInBrowser exec "!open" ExtractUrlFromCurrentLine()
nnoremap <leader>ou :execute "OpenUrlOnCurrentLineInBrowser"<cr>

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

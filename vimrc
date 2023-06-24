set nocompatible

"""""""""""""""""""""""""""""""""
" PLUGINS: START
"""""""""""""""""""""""""""""""""
call plug#begin('~/.vim/plugged')

"""""""""""""""""""""""""""""""""
" Vim color schemes
"""""""""""""""""""""""""""""""""
Plug 'w0ng/vim-hybrid'

"""""""""""""""""""""""""""""""""
" Vim Status Bar
"""""""""""""""""""""""""""""""""
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

"""""""""""""""""""""""""""""""""
" Project Navigation
"""""""""""""""""""""""""""""""""
" Ack command
Plug 'mileszs/ack.vim'

" File searching w/fzf
Plug 'junegunn/fzf'
Plug 'junegunn/fzf.vim'

"""""""""""""""""""""""""""""""""
" File Navigation
"""""""""""""""""""""""""""""""""
" Highlight all search pattern matches
Plug 'haya14busa/incsearch.vim'

" file tree navigation
Plug 'nvim-tree/nvim-web-devicons'
Plug 'nvim-tree/nvim-tree.lua'

" Quick Navigation
Plug 'Lokaltog/vim-easymotion'
Plug 'haya14busa/incsearch-easymotion.vim'

"""""""""""""""""""""""""""""""""
" File management
"""""""""""""""""""""""""""""""""
" Reload file when changed and buffer out of date
Plug 'djoshea/vim-autoread'

" UNIX helpers
Plug 'tpope/vim-eunuch'

"""""""""""""""""""""""""""""""""
" Tabs
"""""""""""""""""""""""""""""""""
" Tab naming, dirty modifier, etc.
Plug 'gcmt/taboo.vim'

" Merge two tabs into 1
Plug 'vim-scripts/Tabmerge'

"""""""""""""""""""""""""""""""""
" Language Specific Highlighting/Functionality
"""""""""""""""""""""""""""""""""
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'vim-ruby/vim-ruby'
Plug 'keith/rspec.vim'
Plug 'slim-template/vim-slim'
Plug 'avakhov/vim-yaml'
Plug 'othree/html5.vim'
Plug 'pangloss/vim-javascript'
Plug 'mxw/vim-jsx'
Plug 'styled-components/vim-styled-components', { 'branch': 'main' }
Plug 'hail2u/vim-css3-syntax'
Plug 'ap/vim-css-color'
Plug 'groenewege/vim-less'
Plug 'jparise/vim-graphql'
Plug 'vim-scripts/nginx.vim'
Plug 'StanAngeloff/php.vim'
Plug 'iamcco/markdown-preview.nvim', { 'do': 'cd app && yarn install' }

"""""""""""""""""""""""""""""""""
" General File Editing
"""""""""""""""""""""""""""""""""
" Improved tab/alignment control
Plug 'godlygeek/tabular'

" Commenting key bindings
Plug 'scrooloose/nerdcommenter'

" Smart abbreviations, subsitution, & coercion
Plug 'tpope/vim-abolish'

" Treat quotes, brackets, etc. in pairs
Plug 'jiangmiao/auto-pairs'

" Automatically add end structures
Plug 'tpope/vim-endwise'

" Keybindings for surrounding stuff
Plug 'tpope/vim-surround'

" Extend the . repeat command for other plugin functions
Plug 'tpope/vim-repeat'

" Git wrapper
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-rhubarb'

" Single/Multiline statement toggle
Plug 'andrewradev/splitjoin.vim'

" Open up documentation for word under cursor
Plug 'keith/investigate.vim'

" Allow creation of custom text objects
Plug 'kana/vim-textobj-user'

" [ & ] keymappings for :allthethings:
Plug 'tpope/vim-unimpaired'

" Autocomplete for search
Plug 'vim-scripts/SearchComplete'

"""""""""""""""""""""""""""""""""
" Javascript File Editing
"""""""""""""""""""""""""""""""""
" node_modules navigation
Plug 'moll/vim-node'

"""""""""""""""""""""""""""""""""
" Ruby File Editing
"""""""""""""""""""""""""""""""""
" Bundle wrapper
Plug 'tpope/vim-bundler'

" Rails file editing/navigation
Plug 'tpope/vim-rails'

" Ruby file editing/navigation
" Plug 'tpope/vim-rake'

" Ruby custom text objects
Plug 'nelstrom/vim-textobj-rubyblock'

"""""""""""""""""""""""""""""""""
" HTML File Editing
"""""""""""""""""""""""""""""""""
" Automatically generate html closing tags
Plug 'alvan/vim-closetag'

" Quick tag creation/editing
Plug 'mattn/emmet-vim'

"""""""""""""""""""""""""""""""""
" File Visualation Helpers
"""""""""""""""""""""""""""""""""
Plug 'Yggdroot/indentLine'
Plug 'machakann/vim-highlightedyank'

"""""""""""""""""""""""""""""""""
" External Integrations
"""""""""""""""""""""""""""""""""
Plug 'rizzatti/dash.vim'

"""""""""""""""""""""""""""""""""
" Tests
"""""""""""""""""""""""""""""""""
Plug 'janko-m/vim-test'

" Plug 'ngmy/vim-rubocop'
" Plug 'vim-scripts/gitignore'

if has('nvim')
  Plug 'kassio/neoterm'
endif

"""""""""""""""""""""""""""""""""
" Task Backgrounding
"""""""""""""""""""""""""""""""""
" Async.vim - Normalized interface to Vim 8 & NeoVim async jobs
Plug 'prabirshrestha/async.vim'

" Synchronous adapters to spawn interactive processes
Plug 'tpope/vim-dispatch'

call plug#end()
"""""""""""""""""""""""""""""""""
" PLUGINS: END
"""""""""""""""""""""""""""""""""

" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal

"""""""""""""""""""""""""""""""""
" VIM SETTINGS
"""""""""""""""""""""""""""""""""

filetype plugin indent on                                                                         " Enable filetype detection, filetype-specific indenting/plugins

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
set lazyredraw                                                                                    " skip redrawing screen in some cases
"set autochdir                                                                                     " automatically set current directory to directory of last opened file
"set wildmode=longest,list                                                                         " tab completion for files/bufferss
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
" set mouse=a                                                                                       " Enable mouse in all modes
set noerrorbells                                                                                  " Disable error bells
"set nostartofline                                                                                 " Don’t reset cursor to start of line when moving around.
set ruler                                                                                         " Show the cursor position
"set shortmess=atI                                                                                 " Don’t show the intro message when starting Vim
set showmode                                                                                      " Show the current mode
set title                                                                                         " Show the filename in the window titlebar
set showcmd                                                                                       " Show the (partial) command as it’s being typed
set scrolloff=3                                                                                   " Start scrolling three lines before the horizontal window border
set signcolumn=yes                                                                                " Always show the signcolumn, otherwise it would shift the text each time diagnostics appear/become resolved
set sidescrolloff=5
set display+=lastline
set shell=/bin/zsh

" highlight current line, but only in active window
augroup CursorLineOnlyInActiveWindow
    autocmd!
    autocmd VimEnter,WinEnter,BufWinEnter * setlocal cursorline
    autocmd WinLeave * setlocal nocursorline
augroup END

" Neovim options
if has('nvim')
  set inccommand=split                                                                            " Live highlight of interactive commands like substitute
endif

"""""""""""""""""""""""""""""""""
" NeoVim Terminal
"""""""""""""""""""""""""""""""""
if has('nvim')
  " Escape to exit terminal mode
  :tnoremap <Esc> <C-\><C-n>

  " Restore navigation between terminal windows/vim windows when in insert
  " mode
  :tnoremap <A-h> <C-\><C-N><C-w>h
  :tnoremap <A-j> <C-\><C-N><C-w>j
  :tnoremap <A-k> <C-\><C-N><C-w>k
  :tnoremap <A-l> <C-\><C-N><C-w>l

  " Paste registers into terminal with alt-r
  :tnoremap <expr> <A-r> '<C-\><C-n>"'.nr2char(getchar()).'pi'

  " Terminal/REPL
  nnoremap TN :Tnew<CR><ESC>
  nnoremap TT :Ttoggle<CR><ESC>
  nnoremap TA :TtoggleAll<CR><ESC>
endif

"""""""""""""""""""""""""""""""""
" ABBREVIATIONS
"""""""""""""""""""""""""""""""""
cabbrev W w
cabbrev Q q
cabbrev Wq wq

"""""""""""""""""""""""""""""""""
" Buffer Navigation Mappings
"""""""""""""""""""""""""""""""""
:inoremap <A-h> <C-\><C-N><C-w>h
:inoremap <A-j> <C-\><C-N><C-w>j
:inoremap <A-k> <C-\><C-N><C-w>k
:inoremap <A-l> <C-\><C-N><C-w>l
:nnoremap <A-h> <C-w>h
:nnoremap <A-j> <C-w>j
:nnoremap <A-k> <C-w>k
:nnoremap <A-l> <C-w>l

"""""""""""""""""""""""""""""""""
" LEADER MAPPINGS
"""""""""""""""""""""""""""""""""
let mapleader = ","

" Edit ~/.vimrc file
nnoremap <leader>ev :vsplit $MYVIMRC<cr>

" Source ~/vimrc file
nnoremap <leader>sv :source $MYVIMRC<cr>

" Save
nnoremap <Leader>w :w<CR>

"""""""""""""""""""""""""""""""""
" NORMAL MAPINGS
"""""""""""""""""""""""""""""""""
" When lines are wrapped, always navigate 1 up/down
nnoremap j gj
nnoremap k gk

" Tab Navigation
nnoremap <C-Left> :tabprevious<CR>
nnoremap <C-Right> :tabnext<CR>
nnoremap <silent> <A-Left> :execute 'silent! tabmove ' . (tabpagenr()-2)<CR>
nnoremap <silent> <A-Right> :execute 'silent! tabmove ' . tabpagenr()<CR>

" toggle relative numbering
nnoremap <C-n> :set rnu!<CR>

"""""""""""""""""""""""""""""""""
" INSERT MAPPINGS
"""""""""""""""""""""""""""""""""
" Delete line while in insert mode
inoremap <c-d> <esc>ddi
" Uppercase current word in insert mode
inoremap <c-u> <esc>viwUi
" New escape key (<esc>, <c-c>, <c-[>)
inoremap jk <esc>

"""""""""""""""""""""""""""""""""
" OPERATION MAPPINGS
"""""""""""""""""""""""""""""""""
onoremap an{ :<c-u>normal! f(va{<cr>
onoremap al{ :<c-u>normal! F(va{<cr>
onoremap in{ :<c-u>normal! f(vi{<cr>
onoremap il{ :<c-u>normal! F(vi{<cr>
onoremap an( :<c-u>normal! f(va(<cr>
onoremap al( :<c-u>normal! F(va(<cr>
onoremap in( :<c-u>normal! f(vi(<cr>
onoremap il( :<c-u>normal! F(vi(<cr>

"""""""""""""""""""""""""""""""""
" PLUGIN MAPPINGS
"""""""""""""""""""""""""""""""""
let g:copilot_node_command = "~/.asdf/installs/nodejs/17.9.1/bin/node"

" Load matchit.vim, but only if the user hasn't installed a newer version.
if !exists('g:loaded_matchit') && findfile('plugin/matchit.vim', &rtp) ==# ''
  runtime! macros/matchit.vim
endif

" nvim-tree/nvim-tree.lua
lua << EOF
  -- disable netrw at the very start of your init.lua
  vim.g.loaded_netrw = 1
  vim.g.loaded_netrwPlugin = 1

  -- set termguicolors to enable highlight groups
  vim.opt.termguicolors = true

  -- empty setup using defaults
  require("nvim-tree").setup()
EOF
noremap \ :NvimTreeToggle<CR>
noremap \| :NvimTreeFindFile<CR>
" TODO: autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif " Automatically close vim when only nerd tree is left open

" scrooloose/nerdcommenter
let g:NERDSpaceDelims = 1
let g:NERDDefaultAlign = 'left'
let g:NERDCommentEmptyLines = 1
let g:NERDTrimTrailingWhitespace = 1

" vim-airline/vim-airline
let g:airline_theme='sol'
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#fnameod = ':t'
let g:airline#extensions#ale#enabled = 1

" rizzatti/dash.vim
nnoremap <Leader>d :Dash<CR>

" iamcco/markdown-preview.nvim
" let g:mkdp_auto_start = 1
nmap <leader>m <Plug>MarkdownPreviewToggle

" janko-m/vim-test
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

" kassio/neoterm
let g:neoterm_default_mod = 'rightbelow'

" neoclide/coc.nvim
" May need for Vim (not Neovim) since coc.nvim calculates byte offset by count
" utf-8 byte sequence
set encoding=utf-8
" Some servers have issues with backup files, see #649
set nobackup
set nowritebackup

" Having longer updatetime (default is 4000 ms = 4s) leads to noticeable
" delays and poor user experience
set updatetime=300

" Always show the signcolumn, otherwise it would shift the text each time
" diagnostics appear/become resolved
set signcolumn=yes

" Use tab for trigger completion with characters ahead and navigate
" NOTE: There's always complete item selected by default, you may want to enable
" no select by `"suggest.noselect": true` in your configuration file
" NOTE: Use command ':verbose imap <tab>' to make sure tab is not mapped by
" other plugin before putting this into your config
inoremap <silent><expr> <TAB>
      \ coc#pum#visible() ? coc#pum#next(1) :
      \ CheckBackspace() ? "\<Tab>" :
      \ coc#refresh()
inoremap <expr><S-TAB> coc#pum#visible() ? coc#pum#prev(1) : "\<C-h>"

" Make <CR> to accept selected completion item or notify coc.nvim to format
" <C-g>u breaks current undo, please make your own choice
inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm()
                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

function! CheckBackspace() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Use <c-space> to trigger completion
if has('nvim')
  inoremap <silent><expr> <c-space> coc#refresh()
else
  inoremap <silent><expr> <c-@> coc#refresh()
endif

" Use `[g` and `]g` to navigate diagnostics
" Use `:CocDiagnostics` to get all diagnostics of current buffer in location list
nmap <silent> [g <Plug>(coc-diagnostic-prev)
nmap <silent> ]g <Plug>(coc-diagnostic-next)

" GoTo code navigation
nmap <silent> gd <Plug>(coc-definition)
nmap <silent> gy <Plug>(coc-type-definition)
nmap <silent> gi <Plug>(coc-implementation)
nmap <silent> gr <Plug>(coc-references)

" Use K to show documentation in preview window
nnoremap <silent> K :call ShowDocumentation()<CR>

function! ShowDocumentation()
  if CocAction('hasProvider', 'hover')
    call CocActionAsync('doHover')
  else
    call feedkeys('K', 'in')
  endif
endfunction

" Highlight the symbol and its references when holding the cursor
autocmd CursorHold * silent call CocActionAsync('highlight')

" Symbol renaming
nmap <leader>rn <Plug>(coc-rename)

" Formatting selected code
xmap <leader>f  <Plug>(coc-format-selected)
nmap <leader>f  <Plug>(coc-format-selected)

augroup mygroup
  autocmd!
  " Setup formatexpr specified filetype(s)
  autocmd FileType typescript,json setl formatexpr=CocAction('formatSelected')
  " Update signature help on jump placeholder
  autocmd User CocJumpPlaceholder call CocActionAsync('showSignatureHelp')
augroup end

" Applying code actions to the selected code block
" Example: `<leader>aap` for current paragraph
xmap <leader>a  <Plug>(coc-codeaction-selected)
nmap <leader>a  <Plug>(coc-codeaction-selected)

" Remap keys for applying code actions at the cursor position
nmap <leader>ac  <Plug>(coc-codeaction-cursor)
" Remap keys for apply code actions affect whole buffer
nmap <leader>as  <Plug>(coc-codeaction-source)
" Apply the most preferred quickfix action to fix diagnostic on the current line
nmap <leader>qf  <Plug>(coc-fix-current)

" Remap keys for applying refactor code actions
nmap <silent> <leader>re <Plug>(coc-codeaction-refactor)
xmap <silent> <leader>r  <Plug>(coc-codeaction-refactor-selected)
nmap <silent> <leader>r  <Plug>(coc-codeaction-refactor-selected)

" Run the Code Lens action on the current line
nmap <leader>cl  <Plug>(coc-codelens-action)

" Map function and class text objects
" NOTE: Requires 'textDocument.documentSymbol' support from the language server
xmap if <Plug>(coc-funcobj-i)
omap if <Plug>(coc-funcobj-i)
xmap af <Plug>(coc-funcobj-a)
omap af <Plug>(coc-funcobj-a)
xmap ic <Plug>(coc-classobj-i)
omap ic <Plug>(coc-classobj-i)
xmap ac <Plug>(coc-classobj-a)
omap ac <Plug>(coc-classobj-a)

" Remap <C-f> and <C-b> to scroll float windows/popups
if has('nvim-0.4.0') || has('patch-8.2.0750')
  nnoremap <silent><nowait><expr> <C-f> coc#float#has_scroll() ? coc#float#scroll(1) : "\<C-f>"
  nnoremap <silent><nowait><expr> <C-b> coc#float#has_scroll() ? coc#float#scroll(0) : "\<C-b>"
  inoremap <silent><nowait><expr> <C-f> coc#float#has_scroll() ? "\<c-r>=coc#float#scroll(1)\<cr>" : "\<Right>"
  inoremap <silent><nowait><expr> <C-b> coc#float#has_scroll() ? "\<c-r>=coc#float#scroll(0)\<cr>" : "\<Left>"
  vnoremap <silent><nowait><expr> <C-f> coc#float#has_scroll() ? coc#float#scroll(1) : "\<C-f>"
  vnoremap <silent><nowait><expr> <C-b> coc#float#has_scroll() ? coc#float#scroll(0) : "\<C-b>"
endif

" Use CTRL-S for selections ranges
" Requires 'textDocument/selectionRange' support of language server
nmap <silent> <C-s> <Plug>(coc-range-select)
xmap <silent> <C-s> <Plug>(coc-range-select)

" Add `:Format` command to format current buffer
command! -nargs=0 Format :call CocActionAsync('format')

" Add `:Fold` command to fold current buffer
command! -nargs=? Fold :call     CocAction('fold', <f-args>)

" Add `:OR` command for organize imports of the current buffer
command! -nargs=0 OR   :call     CocActionAsync('runCommand', 'editor.action.organizeImport')

" Add (Neo)Vim's native statusline support
" NOTE: Please see `:h coc-status` for integrations with external plugins that
" provide custom statusline: lightline.vim, vim-airline
set statusline^=%{coc#status()}%{get(b:,'coc_current_function','')}

" Mappings for CoCList
" Show all diagnostics
nnoremap <silent><nowait> <space>a  :<C-u>CocList diagnostics<cr>
" Manage extensions
nnoremap <silent><nowait> <space>e  :<C-u>CocList extensions<cr>
" Show commands
nnoremap <silent><nowait> <space>c  :<C-u>CocList commands<cr>
" Find symbol of current document
nnoremap <silent><nowait> <space>o  :<C-u>CocList outline<cr>
" Search workspace symbols
nnoremap <silent><nowait> <space>s  :<C-u>CocList -I symbols<cr>
" Do default action for next item
nnoremap <silent><nowait> <space>j  :<C-u>CocNext<CR>
" Do default action for previous item
nnoremap <silent><nowait> <space>k  :<C-u>CocPrev<CR>
" Resume latest coc list
nnoremap <silent><nowait> <space>p  :<C-u>CocListResume<CR>

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

" keith/investigate.vim
let g:investigate_use_dash=1

" mileszs/ack.vim
let g:ackprg = 'rg --hidden --vimgrep'                                                            " Use the 'silver surfer' when grepping


" tpope/vim-rhubarb
let g:github_enterprise_urls = ['https://github.csnzoo.com']

" gcmt/taboo.vim
let g:taboo_tab_format = " %W - %f%m "
let g:taboo_renamed_tab_format = " %W - :Tab%l]%m "

" Yggdroot/indentLine
let g:indentLine_setColors = 1
let g:indentLine_char = '│'
let g:vim_json_conceal=0

" mxw/vim-jsx
let g:jsx_ext_required = 0                                                                        " Allow JSX in normal JS files

" moll/vim-node
autocmd User Node if &filetype == "javascript" | setlocal expandtab | endif

" hail2u/vim-css3-syntax
augroup VimCSS3Syntax
  autocmd!

  autocmd FileType css setlocal iskeyword+=-
augroup END

" alvan/vim-closetag
let g:closetag_filenames = '*.html,*.xhtml,*.phtml,*.html.erb,*.html.slim'
let g:closetag_xhtml_filenames = '*.xhtml,*.jsx,*html.erb,*.html.slim'

" OmniSharp/omnisharp-vim
" Use the stdio OmniSharp-roslyn server
let g:OmniSharp_server_stdio = 1
" Timeout in seconds to wait for a response from the server
let g:OmniSharp_timeout = 5
" Don't autoselect first omnicomplete option, show options even if there is only
" one (so the preview documentation is accessible). Remove 'preview' if you
" don't want to see any documentation whatsoever.
set completeopt=longest,menuone,preview
" Update semantic highlighting after all text changes
let g:OmniSharp_highlight_types = 3

" w0rp/ale configurations
" https://github.com/w0rp/ale#5xii-how-can-i-check-jsx-files-with-both-stylelint-and-eslint
augroup FiletypeGroup
    autocmd!
    au BufNewFile,BufRead *.jsx set filetype=javascript.jsx
augroup END

" junegunn/fzf
nnoremap <leader>f :FZF!<cr>
nnoremap <leader>e :Find!<cr>
nnoremap <leader>c :FindCursor!<cr>
command! -bang -nargs=* Find call fzf#vim#grep('rg --column --line-number --color "always" '.shellescape(<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)
command! -bang -nargs=* FindCursor call fzf#vim#grep('rg --column --line-number --no-heading --color "always" '.shellescape(empty(<q-args>)?expand("<cword>"):<q-args>), 1, fzf#vim#with_preview('right:50%'), <bang>0)
if has('nvim')                                                                                    " Neovim - Esc to close FZF window
  autocmd FileType fzf tnoremap <buffer> <ESC> <C-c>
endif

" vim-scripts/Tabmerge
nnoremap <leader>tm :execute "Tabmerge left"<cr>

"""""""""""""""""""""""""""""""""
" THEMES
"""""""""""""""""""""""""""""""""
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

"nmap <leader>T :enew<cr>                " To open a new empty buffer; replaces :tabnew
"nmap <leader>bq :bp <BAR> bd #<CR>      " Close current buffer and move to previous one, replicates idea of closing tab
"nmap <leader>bl :ls<CR>                 " Show all open buffers and their status
"map q: :q                               " stop annoying window from popping up

"""""""""""""""""""""""""""""""""
" File Treatment
"""""""""""""""""""""""""""""""""
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

"""""""""""""""""""""""""""""""""
" RANDOM
"""""""""""""""""""""""""""""""""
function! ExtractUrlFromCurrentLine()
  return matchstr(getline("."), "http[^ ]*")
endfunction
command! OpenUrlOnCurrentLineInBrowser exec "!open" ExtractUrlFromCurrentLine()
nnoremap <leader>ou :execute "OpenUrlOnCurrentLineInBrowser"<cr>

augroup GitRebaseMode
  autocmd!

  autocmd FileType gitrebase nnoremap <buffer> <leader>s :2,$s/^\w\+ /s /<CR>
  autocmd FileType gitrebase nnoremap <buffer> <leader>f :2,$s/^\w\+ /f /<CR>
augroup END

" when in diff mode
if &diff
  set diffopt+=iwhite
endif

"""""""""""""""""""""""""""""""""
" PERSISTENT UNDO
"""""""""""""""""""""""""""""""""
" Keep undo history across sessions, by storing in file.
if has('persistent_undo')
  set undodir=~/.vim/backups
  set undofile
endif

"""""""""""""""""""""""""""""""""
" Troubleshooting
"""""""""""""""""""""""""""""""""
" Show which highlight groups apply to the item under the cursor
" https://jordanelver.co.uk/blog/2015/05/27/working-with-vim-colorschemes/
nmap <leader>sp :call <SID>SynStack()<CR>
function! <SID>SynStack()
  if !exists("*synstack")
    return
  endif
  echo map(synstack(line('.'), col('.')), 'synIDattr(v:val, "name")')
endfunc

com! FormatJSON %!python -m json.tool

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

let $LOCALFILE=expand("~/.vimrc.local")
if filereadable($LOCALFILE)
    source $LOCALFILE
endif

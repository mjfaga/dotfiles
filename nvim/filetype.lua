vim.filetype.add({
  filename = {
    [".env"] = "dotenv",
  },
  pattern = {
    ["%.env%..*"] = "dotenv",
  },
})

-- Use sh syntax highlighting for dotenv files
vim.api.nvim_create_autocmd("FileType", {
  pattern = "dotenv",
  callback = function()
    vim.bo.syntax = "sh"
  end,
})

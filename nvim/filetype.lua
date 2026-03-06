vim.filetype.add({
  filename = {
    [".env"] = "dotenv",
  },
  pattern = {
    ["%.env%..*"] = "dotenv",
  },
})

-- Phrase Board: classroom phrases, eight to a page. One press speaks one, so
-- the class hears real English used for real purposes all day.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local packs = require("core.packs")
local T = require("teacher.common")

local Board = {}
Board.__index = Board

function Board.new()
  local self = setmetatable({ t = 0, page = 1, sel = 1 }, Board)
  local pack = T.pack()
  self.pages = pack and pack.phrases and packs.read(pack, pack.phrases) or {}
  for _, page in ipairs(self.pages) do
    for _, p in ipairs(page.phrases or {}) do
      p.audio = packs.clips(pack, p.audio)
      p.fa_audio = packs.clips(pack, p.fa_audio)
    end
  end
  return self
end

function Board:leave() T.stop() end
function Board:update(dt) self.t = self.t + dt end

function Board:input(b)
  local page = self.pages[self.page]
  if b == "b" then app.pop() return end
  if not page then return end
  local n = #page.phrases
  local p = page.phrases[self.sel]
  if b == "a" then audio.say(p.audio) self.spoken = self.sel
  elseif b == "x" then audio.say(p.audio, { slow = true }) self.spoken = self.sel
  elseif b == "y" then audio.say(p.fa_audio)
  elseif b == "l" or b == "r" then
    self.page = (self.page - 1 + (b == "l" and -1 or 1)) % #self.pages + 1
    self.sel = 1
    sfx.play("flip")
  else
    local sel = self.sel
    if b == "up" then sel = sel - 2 elseif b == "down" then sel = sel + 2
    elseif b == "left" then sel = sel - 1 elseif b == "right" then sel = sel + 1 end
    if sel >= 1 and sel <= n and sel ~= self.sel then
      self.sel = sel
      sfx.play("move")
    end
  end
end

function Board:draw()
  T.header("tool_phrases")
  local page = self.pages[self.page]
  if not page then return end
  -- page tabs, switched with L and R
  ui.badge("l", 26, 68, 13)
  ui.badge("r", 614, 68, 13)
  for i = 1, #self.pages do
    ui.set(i == self.page and ui.c.teacher or ui.c.line)
    love.graphics.circle("fill", 320 + (i - (#self.pages + 1) / 2) * 22, 68, i == self.page and 8 or 6)
  end
  ui.set(ui.c.ink)
  if page.title_fa and page.title_fa[1] then text.fa(page.title_fa, 340, 50, 250, 24, "right", true) end
  for i, p in ipairs(page.phrases) do
    local col, row = (i - 1) % 2, math.floor((i - 1) / 2)
    local x, y = 14 + col * 310, 90 + row * 87
    local selected = i == self.sel
    ui.card(x, y, 302, 80, { selected = selected, fill = selected and ui.c.shade or ui.c.paper })
    if selected and audio.busy() and self.spoken == i then ui.speaker(x + 280, y + 18, 24, self.t, ui.c.teacher) end
    ui.set(ui.c.ink)
    text.centered("bold", p.text, x + 6, y + 2, 290, 44, 30, 20)
    ui.set(ui.c.soft)
    if p.fa and p.fa[1] then text.centered("fa", p.fa[1], x + 6, y + 40, 290, 38, 24, 20) end
  end
  T.hints({ { "a", "hint_play" }, { "x", "hint_slow" }, { "y", "hint_meaning" } })
end

return Board

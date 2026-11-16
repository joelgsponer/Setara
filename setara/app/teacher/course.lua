-- Teacher's Course: her own English course (every lesson as a private
-- preview, in order) and five-minute teaching tips in Dari audio.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local T = require("teacher.common")

local Course = {}
Course.__index = Course

function Course.new()
  local self = setmetatable({ t = 0, tab = 1, sel = 1 }, Course)
  local pack = T.pack()
  self.lessons = pack and type(pack.lessons) == "table" and pack.lessons or {}
  local tips = pack and type(pack.tips) == "string" and packs.read(pack, pack.tips)
  self.tips = type(tips) == "table" and tips or {}
  for _, tip in ipairs(self.tips) do tip.audio = packs.clips(pack, tip.audio) end
  -- every chapter of every teacher's guide on the card, subject by subject
  self.guide = {}
  for _, gp in ipairs(packs.guides) do
    for index, chapter in ipairs(type(gp.chapters) == "table" and gp.chapters or {}) do
      self.guide[#self.guide + 1] = { pack = gp, index = index, chapter = chapter }
    end
  end
  return self
end

function Course:leave() T.stop() end
function Course:update(dt) self.t = self.t + dt end

function Course:list() return self.tab == 1 and self.lessons or self.tab == 2 and self.tips or self.guide end

function Course:input(b)
  if self.reading then
    if b == "b" then T.stop() self.reading = nil
    elseif b == "a" then audio.say(self.reading.audio) end
    return
  end
  local list = self:list()
  if b == "b" then app.pop()
  elseif b == "left" or b == "right" or b == "l" or b == "r" then
    local step = (b == "left" or b == "l") and 1 or -1   -- the tabs run from right to left
    self.tab = (self.tab - 1 + step) % 3 + 1
    self.sel = 1
    sfx.play("flip")
  elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
  elseif b == "down" and self.sel < #list then self.sel = self.sel + 1 sfx.play("move")
  elseif b == "a" and list[self.sel] then
    if self.tab == 1 then
      app.push(require("teacher.preview").new(self.sel))
    elseif self.tab == 3 then
      local item = list[self.sel]
      app.push(require("teacher.guide").new(item.pack, item.index))
    else
      self.reading = list[self.sel]
      store.count_teacher("tip")
      audio.say(self.reading.audio)
    end
  end
end

function Course:draw()
  T.header("tool_course")
  if self.reading then
    ui.guide(70, 110, 1.4, audio.busy() and "talk" or "idle", self.t)
    ui.set(ui.c.ink)
    if self.reading.title_fa and self.reading.title_fa[1] then
      text.fa(self.reading.title_fa, 130, 56, 496, 30, "right", true)
    end
    ui.card(14, 150, 612, 284, { border = ui.c.line })
    ui.set(ui.c.ink)
    love.graphics.setScissor()
    text.fa(self.reading.fa or {}, 26, 154, 588, 24)
    T.hints({ { "a", "hint_play" } })
    return
  end
  for tab, key in ipairs({ "course_lessons", "course_tips", "course_guide" }) do
    local x = 14 + (3 - tab) * 206
    ui.card(x, 52, 200, 44, { fill = tab == self.tab and ui.c.teacher or ui.c.paper, border = ui.c.teacher, radius = 10 })
    ui.set(tab == self.tab and ui.c.white or ui.c.ink)
    local s = T.S(key)
    if s.fa and s.fa[1] then text.centered("fabold", s.fa[1], x, 50, 200, 44, 22) end
  end
  local list = self:list()
  local first = math.max(1, math.min(self.sel - 2, #list - 4))
  local reached = T.course_reached()
  for i = first, math.min(#list, first + 4) do
    local item = list[i]
    local y = 106 + (i - first) * 66
    ui.card(14, y, 612, 60, { selected = i == self.sel, fill = i == self.sel and ui.c.shade or ui.c.paper })
    if self.tab == 3 then
      -- the subject's colour and the level, then the chapter
      local gp = item.pack
      ui.set(ui.c[gp.subject or "en"] or ui.c.teacher)
      love.graphics.rectangle("fill", 22, y + 8, 44, 44, 8, 8)
      ui.set(ui.c.white)
      text.centered("bold", tostring(gp.level or ""), 22, y + 8, 44, 44, 26)
      ui.set(ui.c.ink)
      text.print(item.chapter.title_en or "", 80, y + 16, 250, "left", 18, true)
      if item.chapter.title_fa and item.chapter.title_fa[1] and text.locale ~= "en" then
        text.fa(item.chapter.title_fa, 320, y + 8, 290, 24, "right", true)
      end
    else
    ui.set(ui.c.teacher)
    text.print(tostring(i), 28, y + 8, 50, "left", 30, true)
    ui.set(ui.c.ink)
    end
    if self.tab == 3 then
    elseif self.tab == 1 then
      text.print(item.title_en or "", 80, y + 16, 280, "left", 20, true)
      if i <= reached then ui.star(596, y + 30, 11, true) end
      if item.title_fa and item.title_fa[1] then text.fa(item.title_fa, 300, y + 8, 270, 24, "right", true) end
    elseif item.title_fa and item.title_fa[1] then
      text.fa(item.title_fa, 80, y + 6, 530, 30, "right", true)
    end
  end
  T.hints({ { "a", "hint_start" }, { "arrows", "hint_next" } })
end

return Course

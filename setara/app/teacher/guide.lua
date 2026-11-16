-- Teacher's guide: one chapter of a guide pack, page by page. Each page is
-- one thing the teacher needs: the goal, what to know, how to explain it, a
-- figure, an example, common mistakes, a classroom activity, the games that
-- practise it, how to check. Left and right turn the pages, A reads the page
-- aloud, B goes back.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local packs = require("core.packs")
local T = require("teacher.common")

local Guide = {}
Guide.__index = Guide

local TAG = { goal = "good", know = "teacher", explain = "teacher", figure = "gold", example = "gold",
  mistake = "bad", activity = "good", games = "en", check = "teacher" }

function Guide.new(pack, index)
  local self = setmetatable({ t = 0, i = 1, pack = pack }, Guide)
  local all = packs.read(pack, pack.guide)
  self.chapter = type(all) == "table" and all[index] or nil
  self.pages = self.chapter and type(self.chapter.pages) == "table" and self.chapter.pages or {}
  for _, page in ipairs(self.pages) do page.audio = packs.clips(pack, page.audio) end
  store.count_teacher("guide")
  return self
end

function Guide:leave() T.stop() end
function Guide:update(dt) self.t = self.t + dt end

function Guide:input(b)
  local page = self.pages[self.i]
  if b == "b" then app.pop()
  elseif (b == "right" or b == "down") and self.i < #self.pages then
    T.stop() self.i = self.i + 1 sfx.play("flip")
  elseif (b == "left" or b == "up") and self.i > 1 then
    T.stop() self.i = self.i - 1 sfx.play("flip")
  elseif (b == "a" or b == "x") and page then
    if audio.busy() then T.stop() else audio.say(page.audio, { slow = b == "x" }) end
  end
end

function Guide:draw()
  local chapter, page = self.chapter, self.pages[self.i]
  T.header("course_guide", chapter and chapter.title_en ~= "" and chapter.title_en or nil)
  if not page then return end
  -- what kind of page this is
  local tag = T.S("guide_" .. tostring(page.kind))
  local color = ui.c[TAG[page.kind] or "teacher"] or ui.c.teacher
  ui.card(14, 50, 612, 40, { fill = ui.mix(ui.c.paper, color, 0.25), border = color, radius = 10 })
  ui.set(ui.c.ink)
  if text.locale == "en" then
    text.print(tag.en or tostring(page.kind), 26, 58, 400, "left", 22, true)
  elseif tag.fa and tag.fa[1] then
    text.fa(tag.fa, 200, 50, 414, 24, "right", true)
  end
  ui.set(ui.c.soft)
  text.print(self.i .. " / " .. #self.pages, 26, 60, 588, text.locale == "en" and "right" or "left", 18, true)
  local y = 98
  if page.img then
    ui.card(200, y, 240, 180, { fill = ui.c.shade, border = ui.c.line, radius = 10 })
    ui.thing(page.img, self.pack.root, 204, y + 3, 232, 174)
    y = y + 188
  end
  local speaking = audio.busy()
  ui.card(14, y, 612, 438 - y, { fill = speaking and ui.mix(ui.c.paper, ui.c.gold, 0.2) or ui.c.paper, border = ui.c.line })
  ui.set(ui.c.ink)
  text.fa(page.fa or {}, 28, y + 6, 584, page.img and 24 or 30, text.locale == "en" and "left" or "right")
  T.hints({ { "a", "hint_play" }, { "arrows", "hint_next" } })
end

return Guide

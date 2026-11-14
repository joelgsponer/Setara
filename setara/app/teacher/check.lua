-- Quick Check: five spoken questions at the end of a lesson. After each one
-- the teacher enters how many hands were right. Only the totals are kept:
-- right answers out of class size, per lesson.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local T = require("teacher.common")

local Check = {}
Check.__index = Check

function Check.new(lesson)
  local self = setmetatable({ t = 0, i = 1, right = 0 }, Check)
  self.lesson = lesson or T.load_lesson()
  self.questions = self.lesson and T.lines(self.lesson, "check") or {}
  self.size = store.progress.settings.class_size
  self.count = math.floor(self.size / 2)
  return self
end

function Check:enter()
  if self.questions[1] then audio.say(self.questions[1].audio) end
end

function Check:leave() T.stop() end
function Check:update(dt) self.t = self.t + dt end

function Check:input(b)
  if self.done or #self.questions == 0 then
    if b == "a" or b == "b" then app.pop(self.done and "checked" or nil) end
    return
  end
  local q = self.questions[self.i]
  if b == "b" then app.pop()
  elseif b == "x" then audio.say(q.audio, { slow = true })
  elseif b == "y" then
    self.show_meaning = true
    audio.say(q.meaning_audio)
  elseif b == "up" then self.count = math.min(self.size, self.count + 1) sfx.play("move")
  elseif b == "down" then self.count = math.max(0, self.count - 1) sfx.play("move")
  elseif b == "right" then self.count = math.min(self.size, self.count + 5) sfx.play("move")
  elseif b == "left" then self.count = math.max(0, self.count - 5) sfx.play("move")
  elseif b == "a" then
    self.right = self.right + self.count
    self.show_meaning = false
    if self.i < #self.questions then
      self.i = self.i + 1
      sfx.play("right")
      audio.say(self.questions[self.i].audio)
    else
      self.done = true
      store.count_check(self.lesson.id, self.right, self.size * #self.questions)
      store.save_stats()
      self.share = self.right / math.max(1, self.size * #self.questions)
      sfx.play("done")
      audio.say(T.S("check_done").audio)
    end
  end
end

function Check:draw()
  T.header("tool_check", self.lesson and (self.lesson.n .. "  " .. (self.lesson.title_en or "")))
  if #self.questions == 0 then return end
  if self.done then
    ui.stars(320, 130, 30, self.share >= 0.8 and 3 or self.share >= 0.5 and 2 or 1)
    ui.set(ui.c.ink)
    text.print(self.right .. " / " .. self.size * #self.questions, 0, 180, 640, "center", 44, true)
    local s = T.S(self.share >= 0.6 and "check_good" or "check_repeat")
    T.dari_card(s.fa or {}, 70, 270, 500)
    T.hints({ { "a", "hint_next" } })
    return
  end
  local q = self.questions[self.i]
  ui.progress(self.i - 1, #self.questions, 220, 64, 200)
  local y = 84
  y = y + T.dari_card(q.teacher_fa, 14, y, 612, 24) + 8
  ui.card(14, y, 612, 64, { fill = ui.c.shade, border = ui.c.line })
  T.english(q.text or "", 22, y + 6, 596, self.t, audio.busy())
  y = y + 72
  if self.show_meaning and q.meaning_fa then
    y = y + T.dari_card(q.meaning_fa, 14, y, 612, 24, ui.mix(ui.c.paper, ui.c.gold, 0.2)) + 8
  end
  -- how many hands were right
  local s = T.S("check_hands")
  ui.set(ui.c.ink)
  if s.fa then text.fa(s.fa, 300, 330, 320, 30, "right", true) end
  ui.card(60, 322, 200, 100, { fill = ui.c.paper, border = ui.c.teacher, width = 4 })
  ui.set(ui.c.teacher)
  text.centered("bold", tostring(self.count), 60, 322, 130, 100, 72)
  ui.set(ui.c.soft)
  text.print("/ " .. self.size, 190, 372, 70, "left", 24)
  ui.arrow("up", 284, 350, 9, ui.c.ink)
  ui.arrow("down", 284, 394, 9, ui.c.ink)
  T.hints({ { "a", "hint_next" }, { "x", "hint_slow" }, { "y", "hint_meaning" } })
end

return Check

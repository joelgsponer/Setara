-- Lesson Runner: one complete lesson, step by step. The screen tells the
-- teacher in Dari what to do; A plays the English through the speaker.
-- The lesson never advances by itself, and the timer counts up: it informs
-- and never rushes her.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local T = require("teacher.common")
local g = love.graphics

local Lesson = {}
Lesson.__index = Lesson

function Lesson.new()
  local self = setmetatable({ t = 0, step = 1, line = 1, step_time = 0, show_meaning = false }, Lesson)
  self.lesson = T.load_lesson()
  return self
end

function Lesson:enter()
  if not self.lesson then return end
  store.count_teacher("lesson_" .. self.lesson.id)
end

function Lesson:leave() T.stop() end

function Lesson:usable() return self.lesson ~= nil end

function Lesson:current()
  local step = self.lesson.steps[self.step]
  return step and step.lines[self.line], step
end

function Lesson:go(step, line)
  T.stop()
  self.tune = false
  self.show_meaning = false
  if step ~= self.step then self.step_time = 0 end
  self.step, self.line = step, line
  sfx.play("move")
end

function Lesson:finish()
  T.stop()
  self.done = true
  store.count_teacher("done_" .. self.lesson.id)
  local n = T.lesson_number()
  if n then T.set_lesson(n + 1) end
  store.save()
  sfx.play("done")
  audio.say(T.S("t_lesson_done").audio)
end

function Lesson:resume(result)
  -- back from the Quick Check: jump past its questions, if it was completed
  if self.checking then
    self.checking = false
    if result ~= "checked" then return end
    local step = self.lesson.steps[self.step]
    local line = self.line
    while step.lines[line] and step.lines[line].kind == "check" do line = line + 1 end
    if step.lines[line] then self.line = line else self:finish() end
  end
end

function Lesson:next_line()
  local _, step = self:current()
  if self.line < #step.lines then
    self:go(self.step, self.line + 1)
  elseif self.step < #self.lesson.steps then
    self:go(self.step + 1, 1)
  else
    self:finish()
  end
end

function Lesson:input(b)
  if not self.lesson or self.done then
    if b == "a" or b == "b" then app.pop() end
    return
  end
  local line, step = self:current()
  if b == "b" then
    app.pop()
  elseif b == "start" then
    app.push(require("scenes.pause").new({ teacher = true }))
  elseif b == "a" then
    if line.kind == "check" then
      -- the five questions are asked in the Quick Check, which records the hands
      self.checking = true
      app.push(require("teacher.check").new(self.lesson))
    elseif line.kind == "tune" then
      self.tune = not self.tune
      if self.tune then sfx.loop("tune") else sfx.stop_loop() end
    elseif line.audio and #line.audio > 0 then
      audio.say(line.audio)
    else
      self:next_line()
    end
  elseif b == "x" then
    if line.audio and #line.audio > 0 then audio.say(line.audio, { slow = true }) end
  elseif b == "y" then
    self.show_meaning = true
    if line.meaning_audio and #line.meaning_audio > 0 then audio.say(line.meaning_audio) end
  elseif b == "down" then
    self:next_line()
  elseif b == "up" then
    if self.line > 1 then
      self:go(self.step, self.line - 1)
    elseif self.step > 1 then
      self:go(self.step - 1, #self.lesson.steps[self.step - 1].lines)
    end
  elseif b == "right" then
    if self.step < #self.lesson.steps then self:go(self.step + 1, 1) end
  elseif b == "left" then
    if self.step > 1 then self:go(self.step - 1, 1) end
  end
end

function Lesson:update(dt)
  self.t = self.t + dt
  if not self.done then self.step_time = self.step_time + dt end
end

function Lesson:draw()
  if not self.lesson then
    T.header("tool_lesson")
    return
  end
  T.header("tool_lesson", self.lesson.n .. "  " .. (self.lesson.title_en or ""))
  if self.done then
    ui.guide(320, 200, 2.4, "happy", self.t)
    local s = T.S("t_lesson_done")
    T.dari_card(s.fa or {}, 120, 300, 400)
    return
  end
  local line, step = self:current()
  -- the six steps
  for i, name in ipairs(T.STEPS) do
    local x = 8 + (i - 1) * 104.5
    local on = name == step.step
    ui.card(x, 50, 100, 40, { fill = on and ui.c.teacher or ui.c.paper,
      border = ui.c.teacher, radius = 8, width = 2 })
    ui.set(on and ui.c.white or ui.c.ink)
    local s = T.S("step_" .. name)
    if s.fa and s.fa[1] then text.centered("fabold", s.fa[1], x, 48, 100, 40, 24) end
  end
  -- time in this step, and the suggested minutes
  ui.set(ui.c.soft)
  text.print(T.timer(self.step_time) .. "  /  " .. (T.MINUTES[step.step] or 5) .. ":00", 14, 96, 200, "left", 20)
  -- which line of the step
  for i = 1, #step.lines do
    ui.set(i == self.line and ui.c.teacher or ui.c.line)
    g.circle("fill", 626 - (i - 1) * 16, 108, 5)
  end
  -- what the teacher does
  local y = 124
  y = y + T.dari_card(line.teacher_fa, 14, y, 612, 30) + 10
  -- what the speaker says
  if line.kind == "tune" then
    ui.card(14, y, 612, 64, { fill = ui.c.shade, border = ui.c.line })
    for i = 0, 2 do
      local up = self.tune and math.sin(self.t * 6 + i) * 6 or 0
      ui.set(ui.c.teacher)
      g.circle("fill", 60 + i * 34, y + 40 + up, 9)
      g.rectangle("fill", 66 + i * 34, y + 12 + up, 4, 28)
    end
    ui.badge("a", 580, y + 32, 16)
  elseif line.text then
    local _, wrapped = text.font("bold", #line.text > 60 and 24 or 30):getWrap(line.text, 536)
    local h = math.max(64, 16 + #wrapped * 42)
    ui.card(14, y, 612, h, { fill = ui.c.shade, border = ui.c.line })
    T.english(line.text, 22, y + 6, 596, self.t, audio.busy())
    y = y + h + 8
    if self.show_meaning and line.meaning_fa then
      T.dari_card(line.meaning_fa, 14, y, 612, 24, ui.mix(ui.c.paper, ui.c.gold, 0.2))
    end
  end
  if line.kind == "check" then
    T.hints({ { "a", "tool_check" }, { "arrows", "hint_next" } })
  else
    T.hints({ { "a", "hint_play" }, { "x", "hint_slow" }, { "y", "hint_meaning" }, { "updown", "hint_next" } })
  end
end

return Lesson

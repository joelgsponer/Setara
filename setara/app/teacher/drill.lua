-- Drill Master: call and response with timed gaps. The speaker says it, the
-- class repeats; then half the room asks and the other half answers, so
-- every child speaks many times in a lesson.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local T = require("teacher.common")
local g = love.graphics

local Drill = {}
Drill.__index = Drill

function Drill.new()
  local self = setmetatable({ t = 0, sel = 1, running = false }, Drill)
  self.lesson = T.load_lesson()
  self.drills = self.lesson and T.lines(self.lesson, "drill") or {}
  return self
end

function Drill:leave() T.stop() end

-- The beats of one drill. A beat either plays audio or is a silent gap in
-- which part of the class speaks; label says who.
function Drill:plan(d)
  local gap = audio.duration(d.audio) * 1.4 + 0.8
  local beats = {}
  local function listen(clips) beats[#beats + 1] = { say = clips, label = "drill_listen" } end
  local function speak(label, seconds) beats[#beats + 1] = { gap = seconds, label = label } end
  for _ = 1, 3 do
    listen(d.audio)
    speak("drill_all", gap)
  end
  if d.answer_audio and #d.answer_audio > 0 then
    local agap = audio.duration(d.answer_audio) * 1.4 + 0.8
    -- model the exchange once, then each half takes a side, then they swap
    listen(d.audio)
    listen(d.answer_audio)
    for _ = 1, 2 do
      speak("drill_left_ask", gap)
      speak("drill_right_answer", agap)
    end
    for _ = 1, 2 do
      speak("drill_right_ask", gap)
      speak("drill_left_answer", agap)
    end
  else
    for _ = 1, 2 do
      listen(d.audio)
      speak("drill_rows", gap)
    end
  end
  return beats
end

function Drill:start()
  local d = self.drills[self.sel]
  if not d then return end
  self.beats = self:plan(d)
  self.beat = 0
  self.running = true
  self:next_beat()
end

function Drill:next_beat()
  self.beat = self.beat + 1
  local b = self.beats[self.beat]
  if not b then
    self.running = false
    sfx.play("done")
    return
  end
  self.left, self.total = b.gap or 0, b.gap or 0
  if b.say then
    audio.say(b.say, { after = 0.25, on_done = function() if self.running then self:next_beat() end end })
  else
    sfx.play("tick")
  end
end

function Drill:stop()
  self.running = false
  audio.stop()
end

function Drill:update(dt)
  self.t = self.t + dt
  if self.running then
    local b = self.beats[self.beat]
    if b and b.gap then
      self.left = self.left - dt
      if self.left <= 0 then self:next_beat() end
    end
  end
end

function Drill:input(b)
  if b == "b" then
    if self.running then self:stop() else app.pop() end
  elseif b == "a" then
    if self.running then self:stop() else self:start() end
  elseif self.running then
    if b == "right" then audio.stop() self:next_beat() end
  elseif b == "x" then
    local d = self.drills[self.sel]
    if d then audio.say(d.audio, { slow = true }) end
  elseif b == "y" then
    local d = self.drills[self.sel]
    if d then audio.say(d.meaning_audio) end
  elseif b == "up" and self.sel > 1 then self.sel = self.sel - 1 sfx.play("move")
  elseif b == "down" and self.sel < #self.drills then self.sel = self.sel + 1 sfx.play("move")
  end
end

-- The room seen from the front: two halves of benches. Lit halves speak.
local function room(label, t)
  local left = label == "drill_all" or label == "drill_left_ask" or label == "drill_left_answer" or label == "drill_rows"
  local right = label == "drill_all" or label == "drill_right_ask" or label == "drill_right_answer" or label == "drill_rows"
  for side = 0, 1 do
    local on = (side == 0 and left) or (side == 1 and right)
    for row = 0, 2 do
      for seat = 0, 3 do
        local x = 150 + side * 190 + seat * 38
        local y = 300 + row * 40
        local wave = on and (label ~= "drill_rows" or math.floor(t * 1.5) % 3 == row)
        ui.set(wave and ui.c.gold or ui.c.line)
        g.circle("fill", x, y - (wave and math.abs(math.sin(t * 6 + seat)) * 4 or 0), 11)
        g.rectangle("fill", x - 12, y + 10, 24, 14, 5, 5)
      end
    end
  end
end

function Drill:draw()
  T.header("tool_drill", self.lesson and (self.lesson.n .. "  " .. (self.lesson.title_en or "")))
  if #self.drills == 0 then
    T.dari_card(T.S("drill_none").fa or {}, 70, 180, 500)
    return
  end
  local d = self.drills[self.sel]
  if not self.running then
    for i, item in ipairs(self.drills) do
      local y = 52 + (i - 1) * 62
      if y < 400 then
        ui.card(14, y, 612, 56, { selected = i == self.sel, fill = i == self.sel and ui.c.shade or ui.c.paper })
        ui.set(ui.c.ink)
        local label = item.text .. (item.answer_text and ("   →   " .. item.answer_text) or "")
        text.centered("bold", label:gsub("\n", " "), 20, y, 600, 56, 24, 16)
      end
    end
    T.hints({ { "a", "hint_start" }, { "x", "hint_slow" }, { "y", "hint_meaning" } })
    return
  end
  local b = self.beats[self.beat] or {}
  ui.card(14, 56, 612, 90, { fill = ui.c.shade, border = ui.c.line })
  T.english((d.text or ""):gsub("\n", " "), 22, 66, 596, self.t, audio.busy())
  if d.answer_text then
    ui.set(ui.c.soft)
    text.print("→ " .. d.answer_text, 82, 108, 530, "left", 24, true)
  end
  local s = T.S(b.label or "drill_listen")
  ui.set(b.gap and ui.c.teacher or ui.c.ink)
  if s.fa then text.fa(s.fa, 20, 156, 600, 36, "center", true) end
  if b.gap then
    ui.set(ui.c.line)
    g.rectangle("fill", 120, 232, 400, 14, 7, 7)
    ui.set(ui.c.gold)
    g.rectangle("fill", 120, 232, 400 * (1 - math.max(0, self.left) / math.max(0.1, self.total)), 14, 7, 7)
  end
  room(b.gap and b.label or "", self.t)
  T.hints({ { "a", "hint_stop" }, { "arrows", "hint_next" } })
end

return Drill

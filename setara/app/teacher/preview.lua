-- Tonight's Preview: the same lesson, alone, in ten minutes. Every English
-- phrase with its Dari meaning, slow playback and a say-it-yourself pause,
-- so the teacher learns the English one lesson ahead of her class.
local ui = require("core.ui")
local text = require("core.text")
local audio = require("core.audio")
local sfx = require("core.sfx")
local store = require("core.store")
local T = require("teacher.common")
local g = love.graphics

local Preview = {}
Preview.__index = Preview

function Preview.new(n)
  local self = setmetatable({ t = 0, i = 1, phase = "idle", wait = 0 }, Preview)
  self.lesson = T.load_lesson(n)
  self.phrases = {}
  local seen = {}
  if self.lesson then
    for _, step in ipairs(self.lesson.steps) do
      for _, line in ipairs(step.lines or {}) do
        if line.text and line.audio and #line.audio > 0 and not seen[line.text] then
          seen[line.text] = true
          self.phrases[#self.phrases + 1] = line
        end
        if line.answer_text and line.answer_audio and #line.answer_audio > 0 and not seen[line.answer_text] then
          seen[line.answer_text] = true
          self.phrases[#self.phrases + 1] = { text = line.answer_text, audio = line.answer_audio }
        end
      end
    end
  end
  return self
end

function Preview:enter()
  if self.lesson then
    store.count_teacher("preview_" .. self.lesson.id)
    store.stats.teacher.course_lesson = math.max(store.stats.teacher.course_lesson or 0, self.lesson.n)
  end
  self:play()
end

function Preview:leave()
  T.stop()
  store.save_stats()
end

-- Hear it, hear the meaning, hear it slowly, say it yourself, hear it again.
function Preview:play()
  local p = self.phrases[self.i]
  if not p then return end
  self.phase = "listen"
  audio.say(p.audio, { after = 0.3, on_done = function()
    self.phase = "meaning"
    audio.say(p.meaning_audio or {}, { after = 0.3, on_done = function()
      self.phase = "slow"
      audio.say(p.audio, { slow = true, after = 0.2, on_done = function()
        self.phase = "say"
        self.wait_total = audio.duration(p.audio, true) * 1.3 + 1
        self.wait = self.wait_total
        audio.say(T.S("t_you_say").audio)
      end })
    end })
  end })
end

function Preview:update(dt)
  self.t = self.t + dt
  if self.phase == "say" and not audio.busy() then
    self.wait = self.wait - dt
    if self.wait <= 0 then
      self.phase = "again"
      audio.say(self.phrases[self.i].audio, { on_done = function() self.phase = "idle" end })
    end
  end
end

function Preview:go(i)
  if i < 1 or i > #self.phrases then return end
  self.i = i
  sfx.play("move")
  self:play()
end

function Preview:input(b)
  local p = self.phrases[self.i]
  if b == "b" then app.pop()
  elseif not p then return
  elseif b == "a" then self:play()
  elseif b == "x" then
    self.phase = "idle"
    audio.say(p.audio, { slow = true })
  elseif b == "y" then
    self.phase = "idle"
    audio.say(p.meaning_audio or {})
  elseif b == "right" or b == "down" then self:go(self.i + 1)
  elseif b == "left" or b == "up" then self:go(self.i - 1)
  end
end

function Preview:draw()
  T.header("tool_preview", self.lesson and (self.lesson.n .. "  " .. (self.lesson.title_en or "")))
  local p = self.phrases[self.i]
  if not p then return end
  ui.set(ui.c.soft)
  text.print(self.i .. " / " .. #self.phrases, 14, 52, 200, "left", 20)
  local _, wrapped = text.font("bold", #p.text > 60 and 24 or 30):getWrap(p.text, 536)
  local h = math.max(80, 24 + #wrapped * 42)
  ui.card(14, 84, 612, h, { fill = ui.c.shade, border = ui.c.line })
  T.english(p.text, 22, 96, 596, self.t, audio.busy() and self.phase ~= "meaning" and self.phase ~= "say")
  local y = 84 + h + 10
  if p.meaning_fa then
    y = y + T.dari_card(p.meaning_fa, 14, y, 612, 30, ui.mix(ui.c.paper, ui.c.gold, 0.2)) + 10
  end
  if self.phase == "say" then
    -- her turn: a bar runs while she says it aloud
    local s = T.S("t_you_say")
    ui.set(ui.c.ink)
    if s.fa then text.fa(s.fa, 100, y, 440, 30, "center", true) end
    ui.set(ui.c.line)
    g.rectangle("fill", 120, y + 56, 400, 14, 7, 7)
    ui.set(ui.c.teacher)
    local share = 1 - math.max(0, self.wait) / math.max(0.1, self.wait_total or 1)
    g.rectangle("fill", 120, y + 56, 400 * share, 14, 7, 7)
  end
  T.hints({ { "a", "hint_play" }, { "x", "hint_slow" }, { "y", "hint_meaning" }, { "arrows", "hint_next" } })
end

return Preview
